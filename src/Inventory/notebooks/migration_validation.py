# Databricks notebook source
# MAGIC %md
# MAGIC # Flyway Migration Validation
# MAGIC 
# MAGIC This notebook validates Flyway migrations and provides detailed status information.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import and Setup

# COMMAND ----------

import json
from datetime import datetime
from flyway_migration_runner import FlywayRunner, create_migration_dashboard

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation Functions

# COMMAND ----------

def validate_migration_integrity(flyway: FlywayRunner) -> dict:
    """Validate migration integrity and return detailed results."""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "validation_passed": True,
        "errors": [],
        "warnings": [],
        "summary": {}
    }
    
    try:
        # Get migration info
        info = flyway.info()
        results["summary"] = info
        
        # Validate migrations
        is_valid = flyway.validate()
        results["validation_passed"] = is_valid
        
        if not is_valid:
            results["errors"].append("Migration validation failed")
        
        # Check for pending migrations
        if info["pending_migrations"] > 0:
            results["warnings"].append(f"{info['pending_migrations']} pending migrations")
        
        # Check migration file consistency
        installed_versions = set(m["version"] for m in info["installed_migrations"])
        file_versions = set(m["version"] for m in info["migration_files"] if m["type"] == "V")
        
        missing_files = installed_versions - file_versions
        if missing_files:
            results["errors"].append(f"Missing migration files for versions: {missing_files}")
            results["validation_passed"] = False
        
        orphaned_files = file_versions - installed_versions
        if orphaned_files:
            results["warnings"].append(f"Uninstalled migration files: {orphaned_files}")
        
    except Exception as e:
        results["validation_passed"] = False
        results["errors"].append(f"Validation error: {str(e)}")
    
    return results

def check_schema_consistency(flyway: FlywayRunner) -> dict:
    """Check schema consistency and table existence."""
    
    results = {
        "schema_check_passed": True,
        "missing_tables": [],
        "table_counts": {},
        "errors": []
    }
    
    try:
        # Get expected tables from migration files
        migration_files = flyway._get_migration_files()
        expected_tables = set()
        
        for migration in migration_files:
            if migration.migration_type == 'V':
                content = flyway._read_migration_content(migration.file_path)
                # Simple regex to find CREATE TABLE statements
                import re
                create_tables = re.findall(r'CREATE TABLE (?:IF NOT EXISTS )?([^\s\(]+)', content, re.IGNORECASE)
                for table in create_tables:
                    # Clean table name
                    table_name = table.strip().replace('`', '').replace('"', '')
                    expected_tables.add(table_name)
        
        # Check if tables exist
        for table in expected_tables:
            try:
                df = spark.sql(f"SELECT COUNT(*) as count FROM {flyway.catalog}.{flyway.schema}.{table}")
                count = df.collect()[0].count
                results["table_counts"][table] = count
            except Exception as e:
                results["missing_tables"].append(table)
                results["schema_check_passed"] = False
                results["errors"].append(f"Table {table} not found: {str(e)}")
        
    except Exception as e:
        results["schema_check_passed"] = False
        results["errors"].append(f"Schema check error: {str(e)}")
    
    return results

def generate_validation_report(flyway: FlywayRunner) -> dict:
    """Generate comprehensive validation report."""
    
    print("=" * 80)
    print("FLYWAY MIGRATION VALIDATION REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Catalog: {flyway.catalog}")
    print(f"Schema: {flyway.schema}")
    print(f"Migration Path: {flyway.migration_path}")
    print("=" * 80)
    
    # Run validations
    integrity_results = validate_migration_integrity(flyway)
    schema_results = check_schema_consistency(flyway)
    
    # Create dashboard
    create_migration_dashboard(flyway)
    
    # Print validation results
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    print(f"\nMigration Integrity: {'✅ PASSED' if integrity_results['validation_passed'] else '❌ FAILED'}")
    if integrity_results['errors']:
        print("Errors:")
        for error in integrity_results['errors']:
            print(f"  - {error}")
    
    if integrity_results['warnings']:
        print("Warnings:")
        for warning in integrity_results['warnings']:
            print(f"  - {warning}")
    
    print(f"\nSchema Consistency: {'✅ PASSED' if schema_results['schema_check_passed'] else '❌ FAILED'}")
    if schema_results['missing_tables']:
        print("Missing Tables:")
        for table in schema_results['missing_tables']:
            print(f"  - {table}")
    
    if schema_results['table_counts']:
        print("\nTable Row Counts:")
        for table, count in schema_results['table_counts'].items():
            print(f"  - {table}: {count:,} rows")
    
    # Overall result
    overall_success = integrity_results['validation_passed'] and schema_results['schema_check_passed']
    print(f"\n{'='*60}")
    print(f"OVERALL VALIDATION: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    print(f"{'='*60}")
    
    return {
        "overall_success": overall_success,
        "integrity_results": integrity_results,
        "schema_results": schema_results,
        "timestamp": datetime.now().isoformat()
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Main Validation Execution

# COMMAND ----------

# Get parameters from notebook
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
migration_path = dbutils.widgets.get("migration_path", "/Workspace/rio/synapse-migration/src/Inventory/sql_deployment")

print(f"Validating Flyway migrations:")
print(f"  Catalog: {catalog}")
print(f"  Schema: {schema}")
print(f"  Migration Path: {migration_path}")

# Initialize Flyway runner
flyway = FlywayRunner(
    catalog=catalog,
    schema=schema,
    migration_path=migration_path
)

# Generate validation report
validation_report = generate_validation_report(flyway)

# Store results for downstream processing
dbutils.notebook.exit(json.dumps(validation_report, default=str))

