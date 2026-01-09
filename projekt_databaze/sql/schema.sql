-- Vytvoření databáze (pokud neexistuje) a nastavení češtiny
CREATE DATABASE IF NOT EXISTS eshop_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE eshop_db;

-- 1. Tabulka Kategorií
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- 2. Tabulka Uživatelů
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL, -- Heslo (pro školní účely jako text)
    is_admin TINYINT(1) DEFAULT 0   -- [BOOL] Splnění podmínky: Logická hodnota
) ENGINE=InnoDB;

-- 3. Tabulka Produktů
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL,           -- [FLOAT] Splnění podmínky: Reálné číslo
    is_active TINYINT(1) DEFAULT 1, -- [BOOL] Skrytí produktu
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB;

-- 4. Tabulka Objednávek
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- [DATETIME] Splnění podmínky: Datum a čas
    status ENUM('new', 'paid', 'shipped', 'cancelled') NOT NULL DEFAULT 'new', -- [ENUM] Splnění podmínky: Výčet
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

-- 5. Tabulka Položek objednávky (Vazební tabulka M:N)
-- [M:N] Spojuje objednávku a produkt (jedna objednávka má více produktů, produkt je ve více objednávkách)
CREATE TABLE IF NOT EXISTS order_items (
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    unit_price FLOAT NOT NULL, -- Ukládáme cenu v době nákupu
    
    PRIMARY KEY (order_id, product_id), -- Složený klíč
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- POHLEDY (VIEWS) - Splnění podmínky: 2x View
-- --------------------------------------------------------

-- View 1: Aktivní produkty (použiješ v aplikaci pro výběr zboží)
CREATE OR REPLACE VIEW v_active_catalog AS
SELECT 
    p.id AS product_id,
    p.name AS product_name,
    p.price,
    c.name AS category_name
FROM products p
JOIN categories c ON p.category_id = c.id
WHERE p.is_active = 1;

-- View 2: Report prodejů (použiješ v záložce Reporty)
-- Agreguje data z více tabulek (SUM, COUNT)
CREATE OR REPLACE VIEW v_sales_report AS
SELECT 
    c.name AS category_name,
    COUNT(oi.product_id) AS items_sold,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN categories c ON p.category_id = c.id
GROUP BY c.name;