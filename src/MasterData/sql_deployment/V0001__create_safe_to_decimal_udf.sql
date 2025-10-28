-- Create a sample Databricks SQL UDF to safely cast strings to numeric
-- Places the function in the `masterdata` schema if available; creates schema when missing

CREATE SCHEMA IF NOT EXISTS masterdata;

CREATE OR REPLACE FUNCTION masterdata.safe_to_decimal(s STRING)
RETURNS DECIMAL(38, 10)
RETURN TRY_CAST(regexp_replace(s, '[^0-9\-\.]', '') AS DECIMAL(38, 10));


