-- MamaEarth Growth Intelligence Pipeline
-- Part 1: Seed raw CSV data
--
-- Run this after schema.sql.
-- The paths below are relative to the project root so the script
-- does not contain a user-specific Windows path.

USE mamaearth_growth;

-- Allow LOCAL INFILE if required by the MySQL client.
SET GLOBAL local_infile = 1;


-- Load customers
LOAD DATA LOCAL INFILE 'data/customers.csv'
INTO TABLE customers
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    customer_id,
    name,
    city,
    city_tier,
    signup_date,
    acquisition_source
);


-- Load products
LOAD DATA LOCAL INFILE 'data/products.csv'
INTO TABLE products
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    product_id,
    product_name,
    category,
    price
);


-- Load orders
-- Blank discount_pct and rating values are loaded as SQL NULL.
LOAD DATA LOCAL INFILE 'data/orders.csv'
INTO TABLE orders
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    order_id,
    customer_id,
    product_id,
    order_date,
    quantity,
    @discount_pct,
    payment_method,
    @rating,
    returned
)
SET
    discount_pct = NULLIF(@discount_pct, ''),
    rating = NULLIF(@rating, '');
