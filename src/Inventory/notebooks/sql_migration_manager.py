# Databricks notebook source
# MAGIC %md
# MAGIC # SQL Migration Manager - Python Implementation
# MAGIC 
# MAGIC This notebook provides a Python-based SQL migration management system for Databricks.
# MAGIC It can execute SQL migrations, track versions, and manage schema changes.
# MAGIC 
# MAGIC ## Features
# MAGIC - Execute SQL migration files
# MAGIC - Track migration versions in Delta tables
# MAGIC - Support for versioned and repeatable migrations
# MAGIC - Rollback functionality
# MAGIC - Migration validation
# MAGIC 
# MAGIC ## Usage
# MAGIC ```python
# MAGIC # Initialize Migration Manager
# MAGIC migration_manager = MigrationManager(
# MAGIC     catalog="your_catalog",
# MAGIC     schema="your_schema", 
# MAGIC     migration_path="/Workspace/path/to/migrations"
# MAGIC )
# MAGIC 
# MAGIC # Run migrations
# MAGIC migration_manager.migrate()
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Libraries and Setup

# COMMAND ----------

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Migration Classes and Data Structures

# COMMAND ----------

@dataclass
class MigrationFile:
    """Represents a migration file."""
    version: str
    description: str
    file_path: str
    migration_type: str  # 'V' for versioned, 'R' for repeatable
    checksum: str = ""
    
    @classmethod
    def from_filename(cls, filename: str, file_path: str) -> 'MigrationFile':
        """Parse migration file from filename.
        
        Args:
            filename: Migration filename (e.g., V1__Create_table.sql)
            file_path: Full path to the file
            
        Returns:
            MigrationFile instance
        """
        # Pattern for versioned migrations: V{version}__{description}.sql
        versioned_pattern = r'^V(\d+(?:\.\d+)*)__(.+)\.sql$'
        # Pattern for repeatable migrations: R__{description}.sql
        repeatable_pattern = r'^R__(.+)\.sql$'
        
        versioned_match = re.match(versioned_pattern, filename)
        if versioned_match:
            version = versioned_match.group(1)
            description = versioned_match.group(2).replace('_', ' ')
            return cls(version, description, file_path, 'V')
        
        repeatable_match = re.match(repeatable_pattern, filename)
        if repeatable_match:
            description = repeatable_match.group(1).replace('_', ' ')
            return cls("", description, file_path, 'R')
        
        raise ValueError(f"Invalid migration filename format: {filename}")

@dataclass
class MigrationRecord:
    """Represents a migration record in the database."""
    version: str
    description: str
    migration_type: str
    script: str
    checksum: str
    installed_by: str
    installed_on: datetime
    execution_time: int
    success: bool

# COMMAND ----------

# MAGIC %md
# MAGIC ## Flyway Runner Class

# COMMAND ----------

class MigrationManager:
    """Python-based SQL migration management system for Databricks."""
    
    def __init__(self, 
                 catalog: str,
                 schema: str,
                 migration_path: str,
                 metadata_schema: str = "migration_metadata",
                 baseline_version: str = "0"):
        """Initialize SQL Migration Manager.
        
        Args:
            catalog: Databricks catalog name
            schema: Target schema for migrations
            migration_path: Path to migration files
            metadata_schema: Schema for migration metadata tables
            baseline_version: Baseline version for existing databases
        """
        self.catalog = catalog
        self.schema = schema
        self.migration_path = migration_path
        self.metadata_schema = metadata_schema
        self.baseline_version = baseline_version
        
        # Initialize metadata tables
        self._create_metadata_tables()
        
    def _create_metadata_tables(self):
        """Create migration metadata tables if they don't exist."""
        
        # Create metadata schema if it doesn't exist
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.{self.metadata_schema}")
        
        # Create schema_version table
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {self.catalog}.{self.metadata_schema}.schema_version (
                version_rank INT,
                installed_rank INT,
                version STRING,
                description STRING,
                migration_type STRING,
                script STRING,
                checksum STRING,
                installed_by STRING,
                installed_on TIMESTAMP,
                execution_time INT,
                success BOOLEAN
            ) USING DELTA
            TBLPROPERTIES (
                'delta.autoOptimize.optimizeWrite' = 'true',
                'delta.autoOptimize.autoCompact' = 'true'
            )
        """)
        
        logger.info(f"Created migration metadata tables in {self.catalog}.{self.metadata_schema}")
    
    def _get_migration_files(self) -> List[MigrationFile]:
        """Get list of migration files from the migration path.
        
        Returns:
            List of MigrationFile objects sorted by version
        """
        migration_files = []
        
        # List files in migration directory
        try:
            files = dbutils.fs.ls(self.migration_path)
            
            for file_info in files:
                filename = file_info.name
                if filename.endswith('.sql'):
                    try:
                        migration = MigrationFile.from_filename(filename, file_info.path)
                        migration_files.append(migration)
                    except ValueError as e:
                        logger.warning(f"Skipping invalid migration file {filename}: {e}")
            
            # Sort by version (versioned first, then repeatable)
            versioned = [m for m in migration_files if m.migration_type == 'V']
            repeatable = [m for m in migration_files if m.migration_type == 'R']
            
            # Sort versioned migrations by version number
            versioned.sort(key=lambda x: [int(v) for v in x.version.split('.')])
            
            # Sort repeatable migrations by description
            repeatable.sort(key=lambda x: x.description)
            
            return versioned + repeatable
            
        except Exception as e:
            logger.error(f"Error reading migration files from {self.migration_path}: {e}")
            return []
    
    def _get_installed_migrations(self) -> List[MigrationRecord]:
        """Get list of already installed migrations.
        
        Returns:
            List of MigrationRecord objects
        """
        try:
            df = spark.sql(f"""
                SELECT version, description, migration_type, script, checksum,
                       installed_by, installed_on, execution_time, success
                FROM {self.catalog}.{self.metadata_schema}.schema_version
                WHERE success = true
                ORDER BY installed_rank
            """)
            
            migrations = []
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
                migrations.append(migration)
            
            return migrations
            
        except Exception as e:
            logger.error(f"Error reading installed migrations: {e}")
            return []
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate checksum for migration content.
        
        Args:
            content: Migration file content
            
        Returns:
            Checksum string
        """
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _read_migration_content(self, file_path: str) -> str:
        """Read migration file content.
        
        Args:
            file_path: Path to migration file
            
        Returns:
            File content as string
        """
        try:
            # Read file using dbutils
            content = dbutils.fs.head(file_path)
            return content
        except Exception as e:
            logger.error(f"Error reading migration file {file_path}: {e}")
            raise
    
    def _execute_migration(self, migration: MigrationFile) -> Tuple[bool, int]:
        """Execute a single migration.
        
        Args:
            migration: MigrationFile to execute
            
        Returns:
            Tuple of (success, execution_time_ms)
        """
        start_time = datetime.now()
        
        try:
            # Read migration content
            content = self._read_migration_content(migration.file_path)
            migration.checksum = self._calculate_checksum(content)
            
            # Split content into individual SQL statements
            statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
            
            # Execute each statement
            for statement in statements:
                if statement:
                    logger.info(f"Executing: {statement[:100]}...")
                    spark.sql(statement)
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.info(f"Migration {migration.version} executed successfully in {execution_time}ms")
            
            return True, execution_time
            
        except Exception as e:
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.error(f"Migration {migration.version} failed: {e}")
            return False, execution_time
    
    def _record_migration(self, migration: MigrationFile, success: bool, execution_time: int):
        """Record migration execution in metadata table.
        
        Args:
            migration: MigrationFile that was executed
            success: Whether migration was successful
            execution_time: Execution time in milliseconds
        """
        try:
            # Get next installed rank
            result = spark.sql(f"""
                SELECT COALESCE(MAX(installed_rank), 0) + 1 as next_rank
                FROM {self.catalog}.{self.metadata_schema}.schema_version
            """).collect()[0]
            next_rank = result.next_rank
            
            # Insert migration record
            spark.sql(f"""
                INSERT INTO {self.catalog}.{self.metadata_schema}.schema_version
                VALUES (
                    {next_rank},
                    {next_rank},
                    '{migration.version}',
                    '{migration.description}',
                    '{migration.migration_type}',
                    '{migration.file_path}',
                    '{migration.checksum}',
                    '{os.environ.get("USER", "unknown")}',
                    current_timestamp(),
                    {execution_time},
                    {str(success).lower()}
                )
            """)
            
            logger.info(f"Recorded migration {migration.version} in metadata table")
            
        except Exception as e:
            logger.error(f"Error recording migration {migration.version}: {e}")
    
    def migrate(self, target_version: Optional[str] = None) -> bool:
        """Run migrations up to target version.
        
        Args:
            target_version: Target version to migrate to (None for latest)
            
        Returns:
            True if all migrations succeeded
        """
        logger.info("Starting SQL migration...")
        
        # Get migration files and installed migrations
        migration_files = self._get_migration_files()
        installed_migrations = self._get_installed_migrations()
        
        if not migration_files:
            logger.warning("No migration files found")
            return True
        
        # Create lookup of installed migrations
        installed_versions = {m.version: m for m in installed_migrations if m.migration_type == 'V'}
        installed_repeatables = {m.description: m for m in installed_migrations if m.migration_type == 'R'}
        
        success = True
        
        # Process versioned migrations
        for migration in migration_files:
            if migration.migration_type == 'V':
                # Check if already installed
                if migration.version in installed_versions:
                    installed = installed_versions[migration.version]
                    # Verify checksum
                    content = self._read_migration_content(migration.file_path)
                    checksum = self._calculate_checksum(content)
                    
                    if checksum != installed.checksum:
                        logger.error(f"Checksum mismatch for migration {migration.version}")
                        success = False
                        break
                    
                    logger.info(f"Migration {migration.version} already installed")
                    continue
                
                # Check if we should stop at target version
                if target_version and migration.version > target_version:
                    logger.info(f"Reached target version {target_version}")
                    break
                
                # Execute migration
                logger.info(f"Executing migration {migration.version}: {migration.description}")
                migration_success, execution_time = self._execute_migration(migration)
                
                # Record migration
                self._record_migration(migration, migration_success, execution_time)
                
                if not migration_success:
                    success = False
                    break
            
            elif migration.migration_type == 'R':
                # Repeatable migrations - always execute if content changed
                content = self._read_migration_content(migration.file_path)
                checksum = self._calculate_checksum(content)
                
                if migration.description in installed_repeatables:
                    installed = installed_repeatables[migration.description]
                    if checksum == installed.checksum:
                        logger.info(f"Repeatable migration {migration.description} unchanged")
                        continue
                
                # Execute repeatable migration
                logger.info(f"Executing repeatable migration: {migration.description}")
                migration_success, execution_time = self._execute_migration(migration)
                
                # Record migration
                self._record_migration(migration, migration_success, execution_time)
                
                if not migration_success:
                    success = False
                    break
        
        if success:
            logger.info("All migrations completed successfully")
        else:
            logger.error("Migration failed")
        
        return success
    
    def info(self) -> Dict:
        """Get migration information.
        
        Returns:
            Dictionary with migration status information
        """
        migration_files = self._get_migration_files()
        installed_migrations = self._get_installed_migrations()
        
        return {
            "migration_files_count": len(migration_files),
            "installed_migrations_count": len(installed_migrations),
            "pending_migrations": len(migration_files) - len(installed_migrations),
            "latest_version": max([m.version for m in installed_migrations if m.migration_type == 'V'], default="None"),
            "migration_files": [{"version": m.version, "description": m.description, "type": m.migration_type} for m in migration_files],
            "installed_migrations": [{"version": m.version, "description": m.description, "installed_on": m.installed_on} for m in installed_migrations]
        }
    
    def validate(self) -> bool:
        """Validate that all installed migrations are still valid.
        
        Returns:
            True if all migrations are valid
        """
        logger.info("Validating migrations...")
        
        migration_files = self._get_migration_files()
        installed_migrations = self._get_installed_migrations()
        
        # Create lookup of migration files
        file_lookup = {m.version: m for m in migration_files if m.migration_type == 'V'}
        file_lookup.update({m.description: m for m in migration_files if m.migration_type == 'R'})
        
        for installed in installed_migrations:
            if installed.migration_type == 'V':
                if installed.version not in file_lookup:
                    logger.error(f"Migration file for version {installed.version} not found")
                    return False
                
                migration = file_lookup[installed.version]
                content = self._read_migration_content(migration.file_path)
                checksum = self._calculate_checksum(content)
                
                if checksum != installed.checksum:
                    logger.error(f"Checksum mismatch for migration {installed.version}")
                    return False
            
            elif installed.migration_type == 'R':
                if installed.description not in file_lookup:
                    logger.error(f"Migration file for repeatable {installed.description} not found")
                    return False
        
        logger.info("All migrations are valid")
        return True

# COMMAND ----------

# MAGIC %md
# MAGIC ## Usage Examples

# COMMAND ----------

# MAGIC %md
# MAGIC ### Initialize and Run Migrations

# COMMAND ----------

# Example usage
# flyway = FlywayRunner(
#     catalog="your_catalog",
#     schema="your_schema",
#     migration_path="/Workspace/path/to/migrations"
# )

# # Run all pending migrations
# success = flyway.migrate()

# # Get migration info
# info = flyway.info()
# print(json.dumps(info, indent=2, default=str))

# # Validate migrations
# is_valid = flyway.validate()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Migration Status Dashboard

# COMMAND ----------

def create_migration_dashboard(migration_manager: MigrationManager):
    """Create a visual dashboard of migration status."""
    
    info = migration_manager.info()
    
    print("=" * 60)
    print("SQL MIGRATION STATUS")
    print("=" * 60)
    print(f"Migration Files: {info['migration_files_count']}")
    print(f"Installed Migrations: {info['installed_migrations_count']}")
    print(f"Pending Migrations: {info['pending_migrations']}")
    print(f"Latest Version: {info['latest_version']}")
    print("=" * 60)
    
    print("\nMIGRATION FILES:")
    for migration in info['migration_files']:
        status = "✓" if migration['version'] in [m['version'] for m in info['installed_migrations']] else "⏳"
        print(f"  {status} {migration['version']} - {migration['description']} ({migration['type']})")
    
    print("\nINSTALLED MIGRATIONS:")
    for migration in info['installed_migrations']:
        print(f"  ✓ {migration['version']} - {migration['description']} ({migration['installed_on']})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Integration with Deployment System

# COMMAND ----------

def run_sql_migrations(catalog: str, schema: str, migration_path: str):
    """Function to be called from deployment orchestrator."""
    
    try:
        # Initialize Migration Manager
        migration_manager = MigrationManager(
            catalog=catalog,
            schema=schema,
            migration_path=migration_path
        )
        
        # Create dashboard
        create_migration_dashboard(migration_manager)
        
        # Run migrations
        print("\nStarting migration execution...")
        success = migration_manager.migrate()
        
        if success:
            print("✅ All migrations completed successfully")
        else:
            print("❌ Migration failed")
            raise Exception("Migration execution failed")
        
        # Validate after migration
        print("\nValidating migrations...")
        is_valid = migration_manager.validate()
        
        if not is_valid:
            print("❌ Migration validation failed")
            raise Exception("Migration validation failed")
        
        print("✅ Migration validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL migration error: {str(e)}")
        raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## Notebook Parameters

# COMMAND ----------

# Get parameters from notebook
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema") 
migration_path = dbutils.widgets.get("migration_path", "/Workspace/rio/synapse-migration/src/Inventory/sql_deployment")

print(f"Running SQL migrations:")
print(f"  Catalog: {catalog}")
print(f"  Schema: {schema}")
print(f"  Migration Path: {migration_path}")

# Run migrations
run_sql_migrations(catalog, schema, migration_path)

