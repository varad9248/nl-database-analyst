-- Drop tables if they exist
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create Users Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    join_date DATE NOT NULL
);

-- Create Products Table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL
);

-- Create Orders Table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    product_id INT REFERENCES products(product_id),
    quantity INT NOT NULL,
    order_date DATE NOT NULL
);

-- Seed Mock Data
INSERT INTO users (name, email, join_date) VALUES
('Aarav Sharma', 'aarav@example.com', '2025-01-15'),
('Ananya Iyer', 'ananya@example.com', '2025-03-22'),
('Vihaan Patel', 'vihaan@example.com', '2025-06-10');

INSERT INTO products (name, category, price, stock) VALUES
('MacBook Pro 14', 'Electronics', 1999.99, 15),
('iPhone 15 Pro', 'Electronics', 999.99, 30),
('Mechanical Keyboard', 'Accessories', 129.99, 50),
('Ergonomic Chair', 'Furniture', 349.99, 10),
('Wireless Mouse', 'Accessories', 79.99, 100);

INSERT INTO orders (user_id, product_id, quantity, order_date) VALUES
(1, 1, 1, '2026-05-01'),
(1, 3, 2, '2026-05-03'),
(2, 2, 1, '2026-05-14'),
(3, 4, 1, '2026-06-01'),
(2, 5, 1, '2026-06-20');