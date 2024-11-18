CREATE DATABASE IF NOT EXISTS warehouse;

-- Use the warehouse database
USE warehouse;

-- Drop tables if they exist (use with caution!).  If they don't exist, this does nothing.
DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;

-- Create Suppliers table
CREATE TABLE IF NOT EXISTS Suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    contact_info VARCHAR(255)
);

-- Create Products table
CREATE TABLE IF NOT EXISTS Products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    supplier_id INT,
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
);

-- Create Locations table
CREATE TABLE IF NOT EXISTS Locations (
    location_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255)
);

-- Create Stock table
CREATE TABLE IF NOT EXISTS Stock (
    stock_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    location_id INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES Locations(location_id)
);

-- Create Orders table
CREATE TABLE IF NOT EXISTS Orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255),
    customer_address VARCHAR(255),
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipping_cost DECIMAL(10, 2),
    total_amount DECIMAL(10, 2)
);

-- Create OrderItems table
CREATE TABLE IF NOT EXISTS OrderItems (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);


-- Add index to OrderItems for faster lookups
CREATE INDEX idx_order_id ON OrderItems(order_id);


-- Sample data (adjust quantities and details as needed)
INSERT INTO Suppliers (name, contact_info) VALUES
('ABC Electronics', 'abc@example.com'),
('XYZ Manufacturing', 'xyz@example.com'),
('Delta Tech', 'delta@example.com'),
('Gamma Industries', 'gamma@example.com'),
('Omega Corp', 'omega@example.com');

INSERT INTO Products (name, description, supplier_id) VALUES
('Laptop', 'High-performance laptop', 1),
('Smartphone', 'Latest Android smartphone', 2),
('Tablet', '10-inch tablet with Wi-Fi', 3),
('Headphones', 'Wireless headphones', 4),
('Keyboard', 'Mechanical gaming keyboard', 5);

INSERT INTO Locations (name, address) VALUES
('Delhi Warehouse', 'New Delhi, India'),
('Mumbai Warehouse', 'Mumbai, India'),
('Bangalore Warehouse', 'Bangalore, India'),
('Chennai Warehouse', 'Chennai, India');

INSERT INTO Stock (product_id, quantity, location_id) VALUES
(1, 50, 1), (2, 100, 1), (3, 20, 1), (4, 15, 1), (5, 30, 1),
(1, 60, 2), (2, 120, 2), (3, 30, 2), (4, 20, 2), (5, 40, 2),
(1, 40, 3), (2, 80, 3), (3, 15, 3), (4, 10, 3), (5, 25, 3),
(1, 50, 4), (2, 100, 4), (3, 20, 4), (4, 15, 4), (5, 30, 4);

-- Example order data
INSERT INTO Orders (customer_name, customer_email, customer_address, status, shipping_cost, total_amount) VALUES
('John Doe', 'john.doe@example.com', '123 Main St', 'pending', 10.00, 150.00);


INSERT INTO OrderItems (order_id, product_id, quantity, price) VALUES
(1, 1, 1, 100.00),
(1, 2, 1, 50.00);


SELECT * FROM Suppliers;
SELECT * FROM Products;
SELECT * FROM Locations;
SELECT * FROM Stock;
SELECT * FROM Orders;
SELECT * FROM OrderItems;