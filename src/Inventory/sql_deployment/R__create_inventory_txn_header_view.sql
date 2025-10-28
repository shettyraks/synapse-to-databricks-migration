-- Repeatable migration: create or replace a view joining transaction and header

CREATE SCHEMA IF NOT EXISTS main.inventory;

CREATE OR REPLACE VIEW main.inventory.v_inventory_txn_header AS
SELECT
    t.transaction_id,
    t.inventory_id,
    h.location_id,
    t.transaction_date,
    t.total_value
FROM main.inventory.inventory_transaction AS t
INNER JOIN main.inventory.inventory_header AS h
    ON t.inventory_id = h.inventory_id;


