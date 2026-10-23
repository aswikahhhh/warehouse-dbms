USE warehouse_management;
INSERT IGNORE INTO employee (emp_id,email_id,name,phone,designation,warehouse_id,password_hash) VALUES
(1,'manager@gmail.com','Rahul Kumar','9876500001','Warehouse Manager',1,NULL),
(2,'anu.staff@example.com','Anu Krishnan','9876500002','Inventory Officer',1,NULL),
(3,'nithin.staff@example.com','Nithin Das','9876500003','Stock Assistant',1,NULL),
(4,'north.manager@example.com','Meera Nair','9876500004','Warehouse Manager',2,NULL),
(5,'north.staff@example.com','Arjun Raj','9876500005','Inventory Officer',2,NULL),
(6,'central.manager@example.com','Fathima P','9876500006','Warehouse Manager',3,NULL);
INSERT IGNORE INTO storage (storage_id,capacity,location,storage_name,warehouse_id) VALUES
(1,500,'Ground floor - Rack A','Electronics Rack A',1),(2,300,'Ground floor - Rack B','Accessories Rack B',1),
(3,450,'First floor - Rack C','Computer Zone C',1),(4,400,'Ground floor - Section N1','North Main Storage',2),
(5,350,'Ground floor - Section C1','Central Storage',3);
INSERT IGNORE INTO product (product_id,name,category,warranty_month,price,warehouse_id) VALUES
(1,'Demo Laptop','Computers',12,45000,1),(2,'Wireless Mouse','Accessories',6,799,1),
(3,'USB-C Charger','Accessories',12,1299,1),(4,'27-inch Monitor','Displays',24,15999,1),
(5,'Mechanical Keyboard','Accessories',12,3499,1),(6,'Wi-Fi Router','Networking',12,2499,1),
(7,'Office Laptop','Computers',12,52000,2),(8,'HDMI Cable','Accessories',3,499,2),
(9,'Laser Printer','Printers',12,12999,3),(10,'SSD 1TB','Storage',36,6999,3);
INSERT IGNORE INTO inventory (inventory_id,product_id,warehouse_id,reorder_level,qty_available) VALUES
(1,1,1,5,20),(2,2,1,15,42),(3,3,1,10,8),(4,4,1,4,12),(5,5,1,8,3),(6,6,1,5,16),
(7,7,2,5,18),(8,8,2,20,60),(9,9,3,3,9),(10,10,3,6,14);
INSERT IGNORE INTO stock_request (sr_id,req_date,status,product_id,qty,warehouse_id,requested_by) VALUES
(1,'2026-10-01','Pending',3,25,1,1),(2,'2026-10-02','Approved',1,10,1,2),
(3,'2026-10-03','Fulfilled',2,20,1,1),(4,'2026-10-04','Pending',8,30,2,4),(5,'2026-10-05','Approved',10,10,3,6);
INSERT IGNORE INTO stock_transfer (st_id,name,received_qty,received_date,sr_id) VALUES
(1,'Wireless Mouse replenishment',20,'2026-10-05',3),(2,'Laptop replenishment',10,'2026-10-06',2),
(3,'SSD replenishment',0,NULL,5),(4,'USB-C Charger request',0,NULL,1);
INSERT IGNORE INTO retail_shop (shop_id,shop_name,address,phone_no) VALUES
(1,'Tech World','Stadium Bypass Road, Palakkad','0491-2300001'),
(2,'Digital Point','Olavakkode, Palakkad','0491-2300002'),
(3,'Smart Devices','Mavoor Road, Kozhikode','0495-2300003'),
(4,'City Electronics','MG Road, Ernakulam','0484-2300004'),
(5,'Campus Computers','College Road, Palakkad','0491-2300005');
INSERT IGNORE INTO sale_order (so_id,status,order_date,product_quantity,product_name,shop_id,warehouse_id) VALUES
(1,'Pending','2026-10-08',4,'Demo Laptop',1,1),(2,'Approved','2026-10-09',10,'Wireless Mouse',2,1),
(3,'Dispatched','2026-10-10',2,'27-inch Monitor',5,1),(4,'Pending','2026-10-11',5,'Office Laptop',3,2),
(5,'Approved','2026-10-12',3,'Laser Printer',4,3);
INSERT IGNORE INTO sale_order_item (sop_id,st_id,name,qty_supplied,supplied_date,so_id,product_id,warehouse_id) VALUES
(1,NULL,'Demo Laptop',0,NULL,1,1,1),(2,1,'Wireless Mouse',10,'2026-10-10',2,2,1),
(3,2,'27-inch Monitor',2,'2026-10-10',3,4,1),(4,NULL,'Office Laptop',0,NULL,4,7,2),
(5,NULL,'Laser Printer',0,NULL,5,9,3);
INSERT IGNORE INTO unit (barcode_id,status,received_date,st_id,storage_id,product_id,inventory_id,sop_id,warehouse_id) VALUES
('PKD-LAP-0001','Available','2026-09-20',2,1,1,1,NULL,1),('PKD-LAP-0002','Available','2026-09-20',2,1,1,1,NULL,1),
('PKD-MOU-0001','Available','2026-09-22',1,2,2,2,NULL,1),('PKD-MOU-0002','Reserved','2026-09-22',1,2,2,2,2,1),
('PKD-CHG-0001','Available','2026-09-25',4,2,3,3,NULL,1),('PKD-KEY-0001','Damaged','2026-09-25',NULL,2,5,5,NULL,1),
('KZD-LAP-0001','Available','2026-09-26',NULL,4,7,7,NULL,2),('EKM-SSD-0001','Available','2026-09-27',NULL,5,10,10,NULL,3);
