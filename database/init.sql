CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    image_url VARCHAR(255),
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- Insert sample bakery products
INSERT INTO products (name, description, price, category) VALUES
('Chocolate Croissant', 'Buttery croissant filled with rich chocolate', 3.50, 'pastry'),
('Sourdough Bread', 'Traditional sourdough with crispy crust', 5.99, 'bread'),
('Blueberry Muffin', 'Moist muffin packed with fresh blueberries', 2.75, 'muffin'),
('Apple Pie', 'Classic apple pie with cinnamon and flaky crust', 12.99, 'pie'),
('Baguette', 'Traditional French baguette with crispy exterior', 3.99, 'bread'),
('Red Velvet Cupcake', 'Soft red velvet with cream cheese frosting', 3.25, 'cake'),
('Cinnamon Roll', 'Warm cinnamon roll with vanilla glaze', 3.99, 'pastry');