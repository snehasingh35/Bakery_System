# Bakery Management System

A containerized bakery management system using Docker, consisting of multiple services working together to demonstrate containerization concepts and Docker orchestration.

## System Architecture

This system consists of the following components:

1. **PostgreSQL Database**: Stores product and order information
2. **Backend API (Flask)**: Provides endpoints for listing products, placing orders, and checking order status
3. **Frontend (React)**: User interface for customers to browse products and place orders
4. **RabbitMQ Message Queue**: Handles asynchronous order processing
5. **Redis Cache**: Caches product listings for improved performance
6. **Worker Service**: Processes orders from the message queue

### Architecture Diagram

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│   Frontend  │ ─────▶ │   Backend   │ ─────▶ │ PostgreSQL  │
│    (React)  │        │   (Flask)   │ ◀───── │  Database   │
└─────────────┘        └─────────────┘        └─────────────┘
                           ▲    ▲                 
                           │    │                 
                 ┌──────────┘    └──────────┐     
                 ▼                           ▼     
           ┌─────────────┐         ┌─────────────┐
           │    Redis    │         │  RabbitMQ   │
           │    Cache    │         │  Message    │
           └─────────────┘         │   Broker    │
                                    └─────────────┘
                                           │                
                                           ▼                
                                ┌─────────────┐
                                │   Worker    │
                                │   Service   │
                                └─────────────┘
      

```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed on your machine
- Git for cloning the repository

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bakery-system
   ```

2. Start the containers:
   ```bash
   docker-compose up -d
   ```

3. Check if all services are running:
   ```bash
   docker-compose ps
   ```

4. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:5000/api/products
   - RabbitMQ Management: http://localhost:15672 (guest/guest)

### Stopping the Application

```bash
docker-compose down
```

To remove all volumes (this will delete all data):
```bash
docker-compose down -v
```

## API Documentation

### List Products

**Endpoint:** `GET /api/products`

**Description:** Returns a list of all bakery products

**Response:**
```json
[
  {
    "id": 1,
    "name": "Chocolate Croissant",
    "description": "Buttery croissant filled with rich chocolate",
    "price": 3.50,
    "category": "pastry"
  },
  ...
]
```

### Place Order

**Endpoint:** `POST /api/orders`

**Description:** Places a new order

**Request Body:**
```json
{
  "customer_name": "John Smith",
  "customer_email": "john@example.com",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ]
}
```

**Response:**
```json
{
  "order_id": 12345,
  "status": "pending"
}
```

### Check Order Status

**Endpoint:** `GET /api/orders/{order_id}`

**Description:** Returns the status and details of an order

**Response:**
```json
{
  "order_id": 12345,
  "customer_name": "John Smith",
  "status": "completed",
  "total_amount": 9.75,
  "created_at": "2025-04-18T14:30:00Z",
  "items": [
    {
      "quantity": 2,
      "name": "Chocolate Croissant",
      "price": 3.50
    },
    {
      "quantity": 1,
      "name": "Blueberry Muffin",
      "price": 2.75
    }
  ]
}
```

## Advanced Features

### Redis Caching

Product listings are cached in Redis for 5 minutes to reduce database load and improve response times.

The cache is automatically invalidated when products are updated or when the TTL expires.

### Worker Service

Orders are processed asynchronously by a dedicated worker service that:
1. Receives orders from RabbitMQ
2. Processes them (simulating payment processing and inventory checks)
3. Updates order status in the database

## Container Resource Management

Resources limits have been configured in the Docker Compose file to ensure proper resource allocation:
- Memory limits for each container
- CPU allocation
- Restart policies to ensure service availability

## Troubleshooting

### Common Issues

1. **Database connection failure:**
   - Check if the PostgreSQL container is running
   - Verify environment variables in the backend service

2. **Redis connection issues:**
   - Ensure Redis container is healthy
   - Check network connectivity between containers

3. **RabbitMQ connection problems:**
   - Verify RabbitMQ is properly initialized
   - Check credentials and connection parameters

### Viewing Logs

```bash
# View logs for all services
docker-compose logs

# View logs for a specific service
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f
```

## Design Decisions

See [design-decisions.md](./docs/design-decisions.md) for detailed information about the design choices made in this project.