CREATE DATABASE IF NOT EXISTS warehouse_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE warehouse_management;
CREATE TABLE IF NOT EXISTS warehouse (
 warehouse_id INT AUTO_INCREMENT PRIMARY KEY, warehouse_name VARCHAR(120) NOT NULL,
 contact_no VARCHAR(30), location VARCHAR(255));
CREATE TABLE IF NOT EXISTS employee (
 emp_id INT AUTO_INCREMENT PRIMARY KEY, email_id VARCHAR(150) NOT NULL UNIQUE,
 name VARCHAR(120) NOT NULL, phone VARCHAR(30), designation VARCHAR(80) NOT NULL DEFAULT 'Employee',
 warehouse_id INT NOT NULL, password_hash VARCHAR(255) NULL,
 FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id));
CREATE TABLE IF NOT EXISTS storage (
 storage_id INT AUTO_INCREMENT PRIMARY KEY, capacity INT NOT NULL DEFAULT 0, location VARCHAR(255),
 storage_name VARCHAR(120) NOT NULL, warehouse_id INT NOT NULL,
 FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id));
CREATE TABLE IF NOT EXISTS product (
 product_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(150) NOT NULL, category VARCHAR(100),
 warranty_month INT NOT NULL DEFAULT 0, price DECIMAL(12,2) NOT NULL DEFAULT 0.00, warehouse_id INT NOT NULL,
 FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id), CHECK (warranty_month>=0), CHECK (price>=0));
CREATE TABLE IF NOT EXISTS inventory (
 inventory_id INT AUTO_INCREMENT PRIMARY KEY, product_id INT NOT NULL, warehouse_id INT NOT NULL,
 reorder_level INT NOT NULL DEFAULT 0, qty_available INT NOT NULL DEFAULT 0,
 last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 UNIQUE KEY uq_inventory_product_warehouse (product_id,warehouse_id),
 FOREIGN KEY (product_id) REFERENCES product(product_id), FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id),
 CHECK (reorder_level>=0), CHECK (qty_available>=0));
CREATE TABLE IF NOT EXISTS stock_request (
 sr_id INT AUTO_INCREMENT PRIMARY KEY, req_date DATE NOT NULL,
 status ENUM('Pending','Approved','Rejected','Fulfilled') NOT NULL DEFAULT 'Pending',
 product_id INT NOT NULL, qty INT NOT NULL, warehouse_id INT NOT NULL, requested_by INT NULL,
 FOREIGN KEY (product_id) REFERENCES product(product_id), FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id),
 FOREIGN KEY (requested_by) REFERENCES employee(emp_id), CHECK (qty>0));
CREATE TABLE IF NOT EXISTS stock_transfer (
 st_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(150) NOT NULL, received_qty INT NOT NULL DEFAULT 0,
 received_date DATE, sr_id INT NOT NULL, FOREIGN KEY (sr_id) REFERENCES stock_request(sr_id), CHECK (received_qty>=0));
CREATE TABLE IF NOT EXISTS retail_shop (
 shop_id INT AUTO_INCREMENT PRIMARY KEY, shop_name VARCHAR(150) NOT NULL, address VARCHAR(255), phone_no VARCHAR(30));
CREATE TABLE IF NOT EXISTS sale_order (
 so_id INT AUTO_INCREMENT PRIMARY KEY, status ENUM('Pending','Approved','Dispatched','Cancelled') NOT NULL DEFAULT 'Pending',
 order_date DATE NOT NULL, product_quantity INT NOT NULL DEFAULT 0, product_name VARCHAR(150),
 shop_id INT NOT NULL, warehouse_id INT NOT NULL, FOREIGN KEY (shop_id) REFERENCES retail_shop(shop_id),
 FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id), CHECK (product_quantity>=0));
CREATE TABLE IF NOT EXISTS sale_order_item (
 sop_id INT AUTO_INCREMENT PRIMARY KEY, st_id INT NULL, name VARCHAR(150) NOT NULL, qty_supplied INT NOT NULL DEFAULT 0,
 supplied_date DATE, so_id INT NOT NULL, product_id INT NOT NULL, warehouse_id INT NOT NULL,
 FOREIGN KEY (st_id) REFERENCES stock_transfer(st_id), FOREIGN KEY (so_id) REFERENCES sale_order(so_id),
 FOREIGN KEY (product_id) REFERENCES product(product_id), FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id),
 CHECK (qty_supplied>=0));
CREATE TABLE IF NOT EXISTS unit (
 barcode_id VARCHAR(100) PRIMARY KEY, status ENUM('Available','Reserved','Dispatched','Damaged') NOT NULL DEFAULT 'Available',
 received_date DATE, st_id INT NULL, storage_id INT NOT NULL, product_id INT NOT NULL, inventory_id INT NULL,
 sop_id INT NULL, warehouse_id INT NOT NULL, FOREIGN KEY (st_id) REFERENCES stock_transfer(st_id),
 FOREIGN KEY (storage_id) REFERENCES storage(storage_id), FOREIGN KEY (product_id) REFERENCES product(product_id),
 FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id), FOREIGN KEY (sop_id) REFERENCES sale_order_item(sop_id),
 FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id));
INSERT IGNORE INTO warehouse (warehouse_id,warehouse_name,contact_no,location) VALUES
(1,'Main Warehouse','0491-000000','Palakkad'),(2,'North Warehouse','0495-111111','Kozhikode'),
(3,'Central Warehouse','0484-222222','Ernakulam');
