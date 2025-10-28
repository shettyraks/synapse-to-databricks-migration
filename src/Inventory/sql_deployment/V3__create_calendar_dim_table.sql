-- Create Calendar Dimension Table
CREATE TABLE IF NOT EXISTS inventory.calendar_dim (
    calendar_date DATE NOT NULL,
    fiscal_year INT NOT NULL,
    fiscal_quarter INT NOT NULL,
    fiscal_month INT NOT NULL,
    fiscal_week INT NOT NULL,
    fiscal_period STRING NOT NULL,
    fiscal_period_start_date DATE NOT NULL,
    fiscal_period_end_date DATE NOT NULL,
    is_month_end BOOLEAN NOT NULL,
    is_quarter_end BOOLEAN NOT NULL,
    is_year_end BOOLEAN NOT NULL,
    week_of_month INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name STRING NOT NULL,
    month_name STRING NOT NULL,
    quarter_name STRING NOT NULL
) USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
