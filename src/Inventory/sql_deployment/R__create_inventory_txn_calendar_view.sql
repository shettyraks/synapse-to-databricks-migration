-- Repeatable migration: create or replace a view joining transaction and calendar

CREATE SCHEMA IF NOT EXISTS inventory;

CREATE OR REPLACE VIEW inventory.v_inventory_txn_calendar AS
SELECT
    t.transaction_id,
    date(t.transaction_date) AS calendar_date,
    c.fiscal_year,
    c.fiscal_month,
    c.fiscal_quarter
FROM inventory.inventory_transaction AS t
INNER JOIN inventory.calendar_dim AS c
    ON date(t.transaction_date) = c.calendar_date;


