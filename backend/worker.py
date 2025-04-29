import pika
import json
import psycopg2
import psycopg2.extras
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection function
def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.environ.get('POSTGRES_HOST', 'db'),
                database=os.environ.get('POSTGRES_DB', 'bakery'),
                user=os.environ.get('POSTGRES_USER', 'postgres'),
                password=os.environ.get('POSTGRES_PASSWORD', 'postgres')
            )
            return conn
        except psycopg2.OperationalError as err:
            retries -= 1
            logger.error(f"Database connection failed. Retrying... ({retries} attempts left)")
            time.sleep(5)
    
    raise Exception("Failed to connect to database after multiple attempts")

# Process an order
def process_order(order_data):
    logger.info(f"Processing order {order_data['order_id']} for {order_data['customer_name']}")
    
    # Simulate processing time - in a real application, this might involve
    # payment processing, inventory checks, etc.
    time.sleep(3)
    
    # Update order status in database
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "UPDATE orders SET status = 'processing' WHERE id = %s",
            (order_data['order_id'],)
        )
        conn.commit()
        logger.info(f"Order {order_data['order_id']} status updated to 'processing'")
        
        # Simulate further processing
        time.sleep(2)
        
        cur.execute(
            "UPDATE orders SET status = 'completed' WHERE id = %s",
            (order_data['order_id'],)
        )
        conn.commit()
        logger.info(f"Order {order_data['order_id']} has been completed")
        
    except Exception as e:
        logger.error(f"Error processing order: {e}")
        conn.rollback()
        
        # Set order to failed
        try:
            cur.execute(
                "UPDATE orders SET status = 'failed' WHERE id = %s",
                (order_data['order_id'],)
            )
            conn.commit()
        except:
            pass
    
    finally:
        cur.close()
        conn.close()

# RabbitMQ callback function
def callback(ch, method, properties, body):
    try:
        order_data = json.loads(body)
        logger.info(f"Received order: {order_data}")
        process_order(order_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        # In a production environment, you might want to implement 
        # retry logic or dead-letter queue handling here
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    # Wait for RabbitMQ to be ready
    retries = 30
    connection = None
    
    while retries > 0:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            break
        except pika.exceptions.AMQPConnectionError:
            retries -= 1
            logger.warning(f"Waiting for RabbitMQ... ({retries} attempts left)")
            time.sleep(2)
    
    if connection is None:
        logger.error("Could not connect to RabbitMQ. Exiting.")
        return
    
    channel = connection.channel()
    channel.queue_declare(queue='order_queue', durable=True)
    
    # Fair dispatch - don't give more than one message to a worker at a time
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='order_queue', on_message_callback=callback)
    
    logger.info("Worker started. Waiting for orders...")
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if connection and connection.is_open:
            connection.close()

if __name__ == '__main__':
    main()
    