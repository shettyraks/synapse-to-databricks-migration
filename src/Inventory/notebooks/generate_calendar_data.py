# Databricks notebook source
# MAGIC %md
# MAGIC # Generate Calendar Data (2015-2030)
# MAGIC 
# MAGIC This notebook generates calendar dimension data for years 2015 to 2030
# MAGIC with fiscal year, quarter, month, week, and related date attributes.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Libraries and Set Parameters

# COMMAND ----------

from datetime import datetime, timedelta
from pyspark.sql import functions as F
from pyspark.sql.types import *

# Get parameters
catalog = dbutils.widgets.get("catalog") if dbutils.widgets.get("catalog") else "main"
schema = dbutils.widgets.get("schema") if dbutils.widgets.get("schema") else "inventory"

print(f"Generating calendar data for catalog: {catalog}, schema: {schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate Calendar Data (2015-2030)

# COMMAND ----------

# Define date range
start_date = datetime(2015, 1, 1)
end_date = datetime(2030, 12, 31)

# Generate all dates in the range
current_date = start_date
calendar_data = []

while current_date <= end_date:
    # Calculate fiscal year (assuming 4-4-5 calendar starting in January)
    fiscal_year = current_date.year
    
    # Calculate fiscal month
    fiscal_month = current_date.month
    
    # Calculate fiscal quarter
    fiscal_quarter = (fiscal_month - 1) // 3 + 1
    
    # Calculate fiscal week within quarter (approximate 4-4-5 calendar)
    # Simplifying for now - in real implementation, this would follow actual 4-4-5 pattern
    days_from_month_start = (current_date - datetime(current_date.year, current_date.month, 1)).days
    fiscal_week = (days_from_month_start // 7) + 1
    
    # Fiscal period (YYYY-MM format)
    fiscal_period = current_date.strftime("%Y-%m")
    
    # Month start and end dates
    fiscal_period_start_date = datetime(current_date.year, current_date.month, 1).date()
    
    # Get last day of month
    if current_date.month == 12:
        fiscal_period_end_date = datetime(current_date.year + 1, 1, 1).date() - timedelta(days=1)
    else:
        fiscal_period_end_date = datetime(current_date.year, current_date.month + 1, 1).date() - timedelta(days=1)
    
    # Quarter end and year end flags
    is_month_end = current_date.day == fiscal_period_end_date.day
    is_quarter_end = current_date.month in [3, 6, 9, 12] and is_month_end
    is_year_end = current_date.month == 12 and is_month_end
    
    # Week of month
    first_day = datetime(current_date.year, current_date.month, 1)
    days_offset = (current_date - first_day).days
    week_of_month = (days_offset // 7) + 1
    
    # Day of week (1=Monday, 7=Sunday)
    day_of_week = current_date.weekday() + 1
    day_name = current_date.strftime("%A")
    month_name = current_date.strftime("%B")
    quarter_name = f"Q{fiscal_quarter}"
    
    calendar_data.append((
        current_date.date(),
        fiscal_year,
        fiscal_quarter,
        fiscal_month,
        fiscal_week,
        fiscal_period,
        fiscal_period_start_date,
        fiscal_period_end_date,
        is_month_end,
        is_quarter_end,
        is_year_end,
        week_of_month,
        day_of_week,
        day_name,
        month_name,
        quarter_name
    ))
    
    current_date += timedelta(days=1)

print(f"Generated {len(calendar_data)} calendar records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create DataFrame and Load to Table

# COMMAND ----------

# Define schema matching the calendar_dim table
calendar_schema = StructType([
    StructField("calendar_date", DateType(), False),
    StructField("fiscal_year", IntegerType(), False),
    StructField("fiscal_quarter", IntegerType(), False),
    StructField("fiscal_month", IntegerType(), False),
    StructField("fiscal_week", IntegerType(), False),
    StructField("fiscal_period", StringType(), False),
    StructField("fiscal_period_start_date", DateType(), False),
    StructField("fiscal_period_end_date", DateType(), False),
    StructField("is_month_end", BooleanType(), False),
    StructField("is_quarter_end", BooleanType(), False),
    StructField("is_year_end", BooleanType(), False),
    StructField("week_of_month", IntegerType(), False),
    StructField("day_of_week", IntegerType(), False),
    StructField("day_name", StringType(), False),
    StructField("month_name", StringType(), False),
    StructField("quarter_name", StringType(), False)
])

# Create DataFrame
df_calendar = spark.createDataFrame(calendar_data, calendar_schema)

print("DataFrame created successfully")
print(f"Total records: {df_calendar.count()}")

# Display sample records
df_calendar.show(20)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Delta Table

# COMMAND ----------

# Write to calendar_dim table (replace existing data)
df_calendar.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable(f"{catalog}.{schema}.calendar_dim")

print(f"Calendar data loaded to {catalog}.{schema}.calendar_dim")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validate Data

# COMMAND ----------

# Verify data
validation_query = spark.sql(f"""
    SELECT 
        MIN(calendar_date) as min_date,
        MAX(calendar_date) as max_date,
        COUNT(*) as total_records,
        COUNT(DISTINCT fiscal_year) as distinct_years
    FROM {catalog}.{schema}.calendar_dim
""")

print("Calendar Data Validation:")
validation_query.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Calendar Generation Completed
# MAGIC 
# MAGIC Successfully generated calendar data for 2015-2030 with fiscal year information.

# COMMAND ----------

# Log completion
dbutils.notebook.exit({
    "status": "SUCCESS",
    "records_generated": df_calendar.count(),
    "date_range": f"2015-01-01 to 2030-12-31",
    "timestamp": datetime.now().isoformat(),
    "catalog": catalog,
    "schema": schema
})

