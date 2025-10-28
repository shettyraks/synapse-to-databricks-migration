-- Repeatable migration: ensures the UDF exists and is up to date on every run

CREATE SCHEMA IF NOT EXISTS masterdata;

CREATE OR REPLACE FUNCTION masterdata.safe_to_decimal(s STRING)
RETURNS DECIMAL(38, 10)
RETURN TRY_CAST(regexp_replace(s, '[^0-9\-\.]', '') AS DECIMAL(38, 10));


