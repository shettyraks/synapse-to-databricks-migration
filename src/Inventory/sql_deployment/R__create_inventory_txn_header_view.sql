-- Repeatable migration: create or replace a view joining transaction and header

CREATE SCHEMA IF NOT EXISTS inventory;

CREATE OR REPLACE VIEW inventory.v_inventory_txn_header AS
SELECT
    t.transaction_id,
    t.inventory_id,
    h.location_id,
    t.transaction_date,
    t.total_value
FROM inventory.inventory_transaction AS t
INNER JOIN inventory.inventory_header AS h
    ON t.inventory_id = h.inventory_id;


