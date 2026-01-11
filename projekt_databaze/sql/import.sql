CREATE DATABASE IF NOT EXISTS eshop_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE eshop_db;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    is_admin TINYINT(1) DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('new', 'paid', 'shipped', 'cancelled') NOT NULL DEFAULT 'new',
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_items (
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    unit_price FLOAT NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB;

CREATE OR REPLACE VIEW v_active_catalog AS
SELECT
    p.id AS product_id,
    p.name AS product_name,
    p.price,
    c.name AS category_name
FROM products p
JOIN categories c ON p.category_id = c.id
WHERE p.is_active = 1;

CREATE OR REPLACE VIEW v_sales_report AS
SELECT
    c.name AS category_name,
    COUNT(oi.product_id) AS items_sold,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN categories c ON p.category_id = c.id
GROUP BY c.name;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE order_items;
TRUNCATE TABLE orders;
TRUNCATE TABLE products;
TRUNCATE TABLE categories;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO users (username, password, is_admin) VALUES
('admin', 'admin123', 1),
('tester', 'user123', 0);

INSERT INTO categories (name) VALUES
('Elektronika'),
('Oblečení'),
('Knihy');

INSERT INTO products (name, price, is_active, category_id) VALUES
('Herní Notebook', 25000.50, 1, 1),
('Myš Bezdrátová', 499.00, 1, 1),
('Kabel HDMI', 150.00, 1, 1),
('Pánské Tričko', 350.00, 1, 2),
('Zimní Bunda', 1200.00, 1, 2),
('Starý Model Telefonu', 5000.00, 0, 1);

INSERT INTO orders (user_id, status, created_at) VALUES
(2, 'shipped', '2023-10-01 10:00:00');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
((SELECT id FROM orders LIMIT 1), 1, 1, 25000.50),
((SELECT id FROM orders LIMIT 1), 2, 2, 499.00);