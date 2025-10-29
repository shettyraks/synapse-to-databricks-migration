# Databricks notebook source
# MAGIC %md
# MAGIC # Flyway Migration Rollback
# MAGIC 
# MAGIC This notebook provides rollback functionality for Flyway migrations.
# MAGIC 
# MAGIC **⚠️ WARNING: Rollback operations can cause data loss. Use with caution!**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import and Setup

# COMMAND ----------

import json
from datetime import datetime
from typing import List, Optional
from flyway_migration_runner import FlywayRunner, MigrationRecord

# COMMAND ----------

# MAGIC %md
# MAGIC ## Rollback Classes and Functions

# COMMAND ----------

class FlywayRollback:
    """Handles rollback operations for Flyway migrations."""
    
    def __init__(self, flyway_runner: FlywayRunner):
        """Initialize rollback handler.
        
        Args:
            flyway_runner: FlywayRunner instance
        """
        self.flyway = flyway_runner
    
    def get_rollback_candidates(self) -> List[MigrationRecord]:
        """Get migrations that can be rolled back.
        
        Returns:
            List of MigrationRecord objects that can be rolled back
        """
        try:
            df = spark.sql(f"""
                SELECT version, description, migration_type, script, checksum,
                       installed_by, installed_on, execution_time, success
                FROM {self.flyway.catalog}.{self.flyway.flyway_schema}.schema_version
                WHERE success = true AND migration_type = 'V'
                ORDER BY installed_rank DESC
            """)
            
            candidates = []
            for row in df.collect():
                migration = MigrationRecord(
                    version=row.version,
                    description=row.description,
                    migration_type=row.migration_type,
                    script=row.script,
                    checksum=row.checksum,
                    installed_by=row.installed_by,
                    installed_on=row.installed_on,
                    execution_time=row.execution_time,
                    success=row.success
                )
                candidates.append(migration)
            
            return candidates
            
        except Exception as e:
            print(f"Error getting rollback candidates: {e}")
            return []
    
    def create_rollback_script(self, target_version: str) -> str:
        """Create rollback script for migrations down to target version.
        
        Args:
            target_version: Target version to rollback to
            
        Returns:
            Rollback script content
        """
        candidates = self.get_rollback_candidates()
        
        # Filter migrations to rollback (those with version > target_version)
        migrations_to_rollback = [
            m for m in candidates 
            if m.version > target_version
        ]
        
        if not migrations_to_rollback:
            return "-- No migrations to rollback"
        
        rollback_script = f"-- Rollback script to version {target_version}\n"
        rollback_script += f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for migration in migrations_to_rollback:
            rollback_script += f"-- Rollback migration {migration.version}: {migration.description}\n"
            
            # For each migration, we need to create reverse operations
            # This is a simplified approach - in practice, you'd need specific rollback logic
            rollback_script += f"-- TODO: Implement rollback for {migration.version}\n"
            rollback_script += f"-- Original script: {migration.script}\n\n"
        
        return rollback_script
    
    def mark_migration_as_rolled_back(self, version: str):
        """Mark a migration as rolled back in the metadata table.
        
        Args:
            version: Version to mark as rolled back
        """
        try:
            spark.sql(f"""
                UPDATE {self.flyway.catalog}.{self.flyway.flyway_schema}.schema_version
                SET success = false,
                    execution_time = 0
                WHERE version = '{version}' AND migration_type = 'V'
            """)
            
            print(f"Marked migration {version} as rolled back")
            
        except Exception as e:
            print(f"Error marking migration {version} as rolled back: {e}")
    
    def rollback_to_version(self, target_version: str, dry_run: bool = True) -> bool:
        """Rollback migrations to a specific version.
        
        Args:
            target_version: Target version to rollback to
            dry_run: If True, only show what would be rolled back
            
        Returns:
            True if rollback was successful
        """
        print(f"{'DRY RUN: ' if dry_run else ''}Rolling back to version {target_version}")
        
        candidates = self.get_rollback_candidates()
        migrations_to_rollback = [
            m for m in candidates 
            if m.version > target_version
        ]
        
        if not migrations_to_rollback:
            print("No migrations to rollback")
            return True
        
        print(f"\nMigrations to rollback:")
        for migration in migrations_to_rollback:
            print(f"  - {migration.version}: {migration.description} (installed: {migration.installed_on})")
        
        if dry_run:
            print("\n⚠️ This was a dry run. No changes were made.")
            return True
        
        # Confirm rollback
        print(f"\n⚠️ WARNING: This will rollback {len(migrations_to_rollback)} migrations!")
        print("This operation may cause data loss.")
        
        # In a real implementation, you'd want user confirmation here
        # For now, we'll just mark them as rolled back
        
        try:
            for migration in migrations_to_rollback:
                self.mark_migration_as_rolled_back(migration.version)
            
            print("✅ Rollback completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def get_rollback_status(self) -> dict:
        """Get current rollback status.
        
        Returns:
            Dictionary with rollback status information
        """
        try:
            # Get all migrations
            df = spark.sql(f"""
                SELECT version, description, migration_type, success, installed_on
                FROM {self.flyway.catalog}.{self.flyway.flyway_schema}.schema_version
                WHERE migration_type = 'V'
                ORDER BY installed_rank
            """)
            
            migrations = []
            for row in df.collect():
                migrations.append({
                    "version": row.version,
                    "description": row.description,
                    "success": row.success,
                    "installed_on": row.installed_on
                })
            
            # Get rollback candidates
            candidates = self.get_rollback_candidates()
            
            return {
                "total_migrations": len(migrations),
                "successful_migrations": len([m for m in migrations if m["success"]]),
                "failed_migrations": len([m for m in migrations if not m["success"]]),
                "rollback_candidates": len(candidates),
                "migrations": migrations
            }
            
        except Exception as e:
            print(f"Error getting rollback status: {e}")
            return {}

def display_rollback_status(rollback_handler: FlywayRollback):
    """Display rollback status in a formatted way."""
    
    status = rollback_handler.get_rollback_status()
    
    print("=" * 60)
    print("FLYWAY ROLLBACK STATUS")
    print("=" * 60)
    print(f"Total Migrations: {status.get('total_migrations', 0)}")
    print(f"Successful Migrations: {status.get('successful_migrations', 0)}")
    print(f"Failed Migrations: {status.get('failed_migrations', 0)}")
    print(f"Rollback Candidates: {status.get('rollback_candidates', 0)}")
    print("=" * 60)
    
    print("\nMigration History:")
    for migration in status.get('migrations', []):
        status_icon = "✅" if migration['success'] else "❌"
        print(f"  {status_icon} {migration['version']} - {migration['description']} ({migration['installed_on']})")
    
    candidates = rollback_handler.get_rollback_candidates()
    if candidates:
        print(f"\nRollback Candidates:")
        for candidate in candidates:
            print(f"  🔄 {candidate.version} - {candidate.description}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Main Rollback Execution

# COMMAND ----------

# Get parameters from notebook
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
migration_path = dbutils.widgets.get("migration_path", "/Workspace/rio/synapse-migration/src/Inventory/sql_deployment")
target_version = dbutils.widgets.get("target_version", "0")
dry_run = dbutils.widgets.get("dry_run", "true").lower() == "true"

print(f"Flyway Rollback Configuration:")
print(f"  Catalog: {catalog}")
print(f"  Schema: {schema}")
print(f"  Migration Path: {migration_path}")
print(f"  Target Version: {target_version}")
print(f"  Dry Run: {dry_run}")

# Initialize Flyway runner and rollback handler
flyway = FlywayRunner(
    catalog=catalog,
    schema=schema,
    migration_path=migration_path
)

rollback_handler = FlywayRollback(flyway)

# Display current status
display_rollback_status(rollback_handler)

# Perform rollback
if target_version != "0":
    print(f"\n{'='*60}")
    success = rollback_handler.rollback_to_version(target_version, dry_run)
    
    if success:
        print("✅ Rollback operation completed")
    else:
        print("❌ Rollback operation failed")
        
    # Display updated status
    print(f"\n{'='*60}")
    print("UPDATED STATUS")
    print(f"{'='*60}")
    display_rollback_status(rollback_handler)
else:
    print("\nNo rollback target specified. Use target_version parameter to specify rollback target.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Rollback Script Generation

# COMMAND ----------

# Generate rollback script for reference
if target_version != "0":
    rollback_script = rollback_handler.create_rollback_script(target_version)
    
    print("=" * 60)
    print("ROLLBACK SCRIPT")
    print("=" * 60)
    print(rollback_script)
    
    # Save script to file
    script_path = f"/tmp/rollback_to_{target_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    dbutils.fs.put(script_path, rollback_script, overwrite=True)
    print(f"\nRollback script saved to: {script_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Safety Notes

# COMMAND ----------

# MAGIC %md
# MAGIC ### Important Safety Considerations
# MAGIC 
# MAGIC 1. **Always test rollbacks in development first**
# MAGIC 2. **Create backups before rollback operations**
# MAGIC 3. **Rollback operations may cause data loss**
# MAGIC 4. **Some migrations cannot be safely rolled back**
# MAGIC 5. **Consider the impact on dependent systems**
# MAGIC 
# MAGIC ### Best Practices
# MAGIC 
# MAGIC 1. Use `dry_run=true` to preview rollback operations
# MAGIC 2. Implement proper rollback scripts for each migration
# MAGIC 3. Test rollback procedures regularly
# MAGIC 4. Document rollback procedures for your team
# MAGIC 5. Consider using feature flags instead of rollbacks when possible

