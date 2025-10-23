# Databricks notebook source
# MAGIC %md
# MAGIC # Inventory ETL Process
# MAGIC 
# MAGIC This notebook processes inventory data from source systems and loads it into the inventory tables.
# MAGIC 
# MAGIC ## Parameters:
# MAGIC - catalog: Target catalog name (default: main)
# MAGIC - schema: Target schema name (default: inventory)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Libraries and Set Parameters

# COMMAND ----------

import pyspark.sql.functions as F
from pyspark.sql.types import *
from datetime import datetime, timedelta
import json

# Get parameters
catalog = dbutils.widgets.get("catalog") if dbutils.widgets.get("catalog") else "main"
schema = dbutils.widgets.get("schema") if dbutils.widgets.get("schema") else "inventory"

print(f"Processing inventory ETL for catalog: {catalog}, schema: {schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Source Data Schema

# COMMAND ----------

# Define schema for source inventory data
inventory_header_schema = StructType([
    StructField("inventory_id", StringType(), True),
    StructField("location_id", StringType(), True),
    StructField("fiscal_period", StringType(), True),
    StructField("fiscal_year", IntegerType(), True),
    StructField("fiscal_month", IntegerType(), True),
    StructField("fiscal_quarter", IntegerType(), True),
    StructField("source_system", StringType(), True),
    StructField("raw_data", StringType(), True)
])

inventory_transaction_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("inventory_id", StringType(), True),
    StructField("upc", StringType(), True),
    StructField("sku", StringType(), True),
    StructField("product_name", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("unit_price", DecimalType(10,2), True),
    StructField("transaction_date", TimestampType(), True),
    StructField("transaction_type", StringType(), True),
    StructField("source_system", StringType(), True),
    StructField("raw_data", StringType(), True)
])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Source Data

# COMMAND ----------

# Simulate loading data from source system (replace with actual source)
# In a real scenario, this would connect to your source database or file system

# Create sample source data
source_header_data = [
    ("INV-2024-004", "LOC-004", "2024-04", 2024, 4, 2, "SYNAPSE", '{"source": "synapse_migration"}'),
    ("INV-2024-005", "LOC-005", "2024-05", 2024, 5, 2, "SYNAPSE", '{"source": "synapse_migration"}'),
]

source_transaction_data = [
    ("TXN-005", "INV-2024-004", "123456789016", "SKU-005", "Migrated Product 1", 150, 22.50, datetime.now(), "INBOUND", "SYNAPSE", '{"source": "synapse_migration"}'),
    ("TXN-006", "INV-2024-004", "123456789017", "SKU-006", "Migrated Product 2", 80, 18.75, datetime.now(), "INBOUND", "SYNAPSE", '{"source": "synapse_migration"}'),
    ("TXN-007", "INV-2024-005", "123456789018", "SKU-007", "Migrated Product 3", 120, 28.99, datetime.now(), "INBOUND", "SYNAPSE", '{"source": "synapse_migration"}'),
]

# Create DataFrames
df_header_source = spark.createDataFrame(source_header_data, inventory_header_schema)
df_transaction_source = spark.createDataFrame(source_transaction_data, inventory_transaction_schema)

print("Source data loaded successfully")
df_header_source.show()
df_transaction_source.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transform Data

# COMMAND ----------

# Transform header data
df_header_transformed = df_header_source.select(
    F.col("inventory_id"),
    F.col("location_id"),
    F.col("fiscal_period"),
    F.col("fiscal_year"),
    F.col("fiscal_month"),
    F.col("fiscal_quarter"),
    F.current_timestamp().alias("created_date"),
    F.current_timestamp().alias("updated_date"),
    F.lit("etl_process").alias("created_by"),
    F.lit("etl_process").alias("updated_by")
)

# Transform transaction data
df_transaction_transformed = df_transaction_source.select(
    F.col("transaction_id"),
    F.col("inventory_id"),
    F.col("upc"),
    F.col("sku"),
    F.col("product_name"),
    F.col("quantity"),
    F.col("unit_price"),
    F.expr("quantity * unit_price").alias("total_value"),
    F.col("transaction_date"),
    F.col("transaction_type"),
    F.current_timestamp().alias("created_date"),
    F.current_timestamp().alias("updated_date"),
    F.lit("etl_process").alias("created_by"),
    F.lit("etl_process").alias("updated_by")
)

print("Data transformation completed")
df_header_transformed.show()
df_transaction_transformed.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data to Target Tables

# COMMAND ----------

# Write to inventory header table
df_header_transformed.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable(f"{catalog}.{schema}.inventory_header")

print("Inventory header data loaded successfully")

# Write to inventory transaction table
df_transaction_transformed.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable(f"{catalog}.{schema}.inventory_transaction")

print("Inventory transaction data loaded successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validate Data Quality

# COMMAND ----------

# Validate data quality
header_count = spark.sql(f"SELECT COUNT(*) as count FROM {catalog}.{schema}.inventory_header").collect()[0]["count"]
transaction_count = spark.sql(f"SELECT COUNT(*) as count FROM {catalog}.{schema}.inventory_transaction").collect()[0]["count"]

print(f"Total inventory headers: {header_count}")
print(f"Total inventory transactions: {transaction_count}")

# Check for data quality issues
quality_checks = spark.sql(f"""
    SELECT 
        'Missing UPC' as check_name,
        COUNT(*) as issue_count
    FROM {catalog}.{schema}.inventory_transaction 
    WHERE upc IS NULL OR upc = ''
    
    UNION ALL
    
    SELECT 
        'Negative Quantity' as check_name,
        COUNT(*) as issue_count
    FROM {catalog}.{schema}.inventory_transaction 
    WHERE quantity < 0
    
    UNION ALL
    
    SELECT 
        'Zero Price' as check_name,
        COUNT(*) as issue_count
    FROM {catalog}.{schema}.inventory_transaction 
    WHERE unit_price <= 0
""")

print("Data Quality Check Results:")
quality_checks.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Summary Report

# COMMAND ----------

# Generate summary report
summary_report = spark.sql(f"""
    SELECT 
        h.fiscal_year,
        h.fiscal_quarter,
        h.fiscal_month,
        COUNT(DISTINCT h.inventory_id) as inventory_count,
        COUNT(t.transaction_id) as transaction_count,
        SUM(t.total_value) as total_inventory_value,
        AVG(t.unit_price) as avg_unit_price
    FROM {catalog}.{schema}.inventory_header h
    LEFT JOIN {catalog}.{schema}.inventory_transaction t ON h.inventory_id = t.inventory_id
    GROUP BY h.fiscal_year, h.fiscal_quarter, h.fiscal_month
    ORDER BY h.fiscal_year, h.fiscal_quarter, h.fiscal_month
""")

print("Inventory Summary Report:")
summary_report.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## ETL Process Completed Successfully
# MAGIC 
# MAGIC The inventory ETL process has completed with the following results:
# MAGIC - Data loaded from source systems
# MAGIC - Data transformed and validated
# MAGIC - Data loaded to target tables
# MAGIC - Data quality checks performed
# MAGIC - Summary report generated

# COMMAND ----------

# Log completion
dbutils.notebook.exit({
    "status": "SUCCESS",
    "records_processed": header_count + transaction_count,
    "timestamp": datetime.now().isoformat(),
    "catalog": catalog,
    "schema": schema
})
