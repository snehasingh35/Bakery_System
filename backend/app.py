from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
import json
import pika
import redis
import time
from decimal import Decimal
from dotenv import load_dotenv  # Import dotenv for loading .env variables

# Load environment variables from .env file
load_dotenv()

# Custom JSON Encoder
class CustomJSONEncoder(Flask.json_encoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float
        return super().default(obj)


app = Flask(__name__)
CORS(app)

# Database connection function
def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'db'),
                database=os.getenv('POSTGRES_DB', 'bakery'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres')
            )
            return conn
        except psycopg2.OperationalError as err:
            retries -= 1
            print(f"Database connection failed. Retrying... ({retries} attempts left)")
            time.sleep(5)
    
    raise Exception("Failed to connect to database after multiple attempts")

# RabbitMQ connection
def get_rabbitmq_connection():
    retries = 5
    while retries > 0:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'rabbitmq'))
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            retries -= 1
            print(f"RabbitMQ connection failed. Retrying... ({retries} attempts left)")
            time.sleep(5)
    
    raise Exception("Failed to connect to RabbitMQ after multiple attempts")

# Redis connection
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'redis'), port=6379, db=0)

# # Custom JSON encoder for Decimal
# class CustomJSONEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Decimal):
#             return float(obj)
#         return super().default(obj)

app.json_encoder = CustomJSONEncoder

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/products', methods=['GET'])
def get_products():
    """List all bakery products with Redis caching"""
    
    # Try to get from cache first
    cache_key = "all_products"
    cached_products = redis_client.get(cache_key)
    
    if cached_products:
        app.logger.info("Serving products from cache")
        return cached_products, 200, {'Content-Type': 'application/json'}
    
    app.logger.info("Cache miss, fetching products from database")
    
    # If not in cache, query database
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM products ORDER BY name")
    products = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert Decimal fields to float
    for product in products:
        for key, value in product.items():
            if isinstance(value, Decimal):
                product[key] = float(value)
    
    # Store in cache for 5 minutes (300 seconds)
    products_json = json.dumps(products, default=str)
    redis_client.setex(cache_key, 300, products_json)
    
    # Return using the same JSON-serialized data we put in the cache
    return products_json, 200, {'Content-Type': 'application/json'}

@app.route('/api/orders', methods=['POST'])
def place_order():
    """Place a new bakery order"""
    data = request.json
    
    # Validate input
    if not all(key in data for key in ['customer_name', 'customer_email', 'items']):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Calculate total amount
    total_amount = 0
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    for item in data['items']:
        cur.execute("SELECT price FROM products WHERE id = %s", (item['product_id'],))
        product = cur.fetchone()
        if not product:
            return jsonify({"error": f"Product with ID {item['product_id']} not found"}), 404
        total_amount += product['price'] * item['quantity']
    
    # Create order
    cur.execute(
        "INSERT INTO orders (customer_name, customer_email, total_amount) VALUES (%s, %s, %s) RETURNING id",
        (data['customer_name'], data['customer_email'], total_amount)
    )
    order_id = cur.fetchone()['id']
    
    # Create order items
    for item in data['items']:
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
            (order_id, item['product_id'], item['quantity'], product['price'])
        )
    
    conn.commit()
    cur.close()
    conn.close()
    
    # Send to RabbitMQ for processing
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue='order_queue', durable=True)
    
    message = {
        'order_id': order_id,
        'customer_name': data['customer_name'],
        'customer_email': data['customer_email'],
        'total_amount': float(total_amount)
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='order_queue',
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
    )
    
    connection.close()
    
    return jsonify({"order_id": order_id, "status": "pending"})

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def check_order_status(order_id):
    """Check the status of an order"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get order details
    cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cur.fetchone()
    
    if not order:
        return jsonify({"error": "Order not found"}), 404
        
    # Get order items
    cur.execute(
        """
        SELECT oi.quantity, p.name, p.price 
        FROM order_items oi 
        JOIN products p ON oi.product_id = p.id 
        WHERE oi.order_id = %s
        """, 
        (order_id,)
    )
    items = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Format response
    result = {
        "order_id": order['id'],
        "customer_name": order['customer_name'],
        "status": order['status'],
        "total_amount": float(order['total_amount']),
        "created_at": order['created_at'].isoformat(),
        "items": items
    }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
