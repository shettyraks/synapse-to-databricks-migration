-- Create Inventory Transaction Table
CREATE TABLE IF NOT EXISTS main.inventory.inventory_transaction (
    transaction_id STRING NOT NULL,
    inventory_id STRING NOT NULL,
    upc STRING NOT NULL,
    sku STRING NOT NULL,
    product_name STRING,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_value DECIMAL(12,2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    transaction_type STRING NOT NULL,
    created_date TIMESTAMP NOT NULL,
    updated_date TIMESTAMP NOT NULL,
    created_by STRING NOT NULL,
    updated_by STRING NOT NULL
) USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
