USE eshop_db;

-- Vyčistíme tabulky (kdybys to spouštěl vícekrát)
DELETE FROM order_items;
DELETE FROM orders;
DELETE FROM products;
DELETE FROM categories;
DELETE FROM users;

-- 1. Vložení Uživatelů
INSERT INTO users (username, password, is_admin) VALUES 
('admin', 'admin123', 1),
('tester', 'user123', 0);

-- 2. Vložení Kategorií
INSERT INTO categories (name) VALUES 
('Elektronika'), 
('Oblečení'), 
('Knihy');

-- 3. Vložení Produktů
INSERT INTO products (name, price, is_active, category_id) VALUES 
('Herní Notebook', 25000.50, 1, 1),
('Myš Bezdrátová', 499.00, 1, 1),
('Kabel HDMI', 150.00, 1, 1),
('Pánské Tričko', 350.00, 1, 2),
('Zimní Bunda', 1200.00, 1, 2),
('Starý Model Telefonu', 5000.00, 0, 1); -- Neaktivní (nebude vidět v nabídce)

-- 4. Vložení jedné hotové objednávky (aby bylo něco vidět v reportu)
INSERT INTO orders (user_id, status, created_at) VALUES 
(2, 'shipped', '2023-10-01 10:00:00');

-- Získání ID poslední objednávky (pro jistotu vložíme natvrdo ID 1, pokud je tabulka prázdná)
-- Položky k objednávce:
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES 
((SELECT id FROM orders LIMIT 1), 1, 1, 25000.50), -- 1x Notebook
((SELECT id FROM orders LIMIT 1), 2, 2, 499.00);   -- 2x Myš