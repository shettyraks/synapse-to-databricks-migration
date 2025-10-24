-- Create Inventory Header Table
CREATE TABLE IF NOT EXISTS main.inventory.inventory_header (
    inventory_id STRING NOT NULL,
    location_id STRING NOT NULL,
    fiscal_period STRING NOT NULL,
    fiscal_year INT NOT NULL,
    fiscal_month INT NOT NULL,
    fiscal_quarter INT NOT NULL,
    created_date TIMESTAMP NOT NULL,
    updated_date TIMESTAMP NOT NULL,
    created_by STRING NOT NULL,
    updated_by STRING NOT NULL
) USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
