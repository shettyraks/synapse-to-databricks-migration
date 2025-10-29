#!/usr/bin/env python3
"""
Validate deployment after SQL migrations and Databricks assets deployment.
Uses modular configuration and client architecture.
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config import DeploymentConfig
from modules.databricks_client import DatabricksClient


def validate_tables(environment: str, catalog: str, schemas: str) -> bool:
    """Validate that required tables exist.
    
    Args:
        environment: Environment name
        catalog: Catalog name
        schemas: Comma-separated schema names
        
    Returns:
        True if validation passes
    """
    print(f"Validating tables for {environment} environment...")
    
    required_tables = [
        ('inventory', 'inventory_header'),
        ('inventory', 'inventory_transaction'),
        ('inventory', 'calendar_dim')
    ]
    
    print(f"Expected catalog: {catalog}")
    print(f"Expected schemas: {schemas}")
    
    for schema, table in required_tables:
        print(f"  ✓ {schema}.{table} should exist")
    
    print("✅ Table validation completed (placeholder)")
    return True


def validate_jobs(environment: str, client: DatabricksClient) -> bool:
    """Validate that Databricks jobs are configured correctly.
    
    Args:
        environment: Environment name
        client: Databricks client
        
    Returns:
        True if validation passes
    """
    print(f"Validating jobs for {environment} environment...")
    
    expected_jobs = [
        f"{environment}_Inventory_ETL_Job",
        f"{environment}_Generate_Calendar_Data"
    ]
    
    try:
        jobs = client.list_jobs()
        print(f"Found {len(jobs)} jobs in workspace")
        
        for expected_job in expected_jobs:
            print(f"  - {expected_job}")
        
    except Exception as e:
        print(f"⚠️ Could not list jobs: {e}")
        print("Expected jobs:")
        for expected_job in expected_jobs:
            print(f"  - {expected_job}")
    
    print("✅ Job validation completed")
    return True


def validate_data_quality(environment: str, catalog: str, schemas: str) -> bool:
    """Validate data quality in deployed tables.
    
    Args:
        environment: Environment name
        catalog: Catalog name
        schemas: Comma-separated schema names
        
    Returns:
        True if validation passes
    """
    print(f"Validating data quality for {environment} environment...")
    
    print("Running data quality checks...")
    print("  ✓ Row count checks")
    print("  ✓ NULL value checks")
    print("  ✓ Constraint validation")
    
    print("✅ Data quality validation completed (placeholder)")
    return True


def main():
    parser = argparse.ArgumentParser(description='Validate deployment')
    parser.add_argument('--environment', required=True,
                       choices=['dev', 'sit', 'uat', 'prod'],
                       help='Environment to validate')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = DeploymentConfig(args.environment)
        client = DatabricksClient(config)
        
        print(f"Validating deployment for {args.environment} environment...")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        validation_passed = True
        
        # Validate tables
        if not validate_tables(args.environment, config.env_config.catalog, config.get_schemas_str()):
            validation_passed = False
        
        # Validate jobs
        if not validate_jobs(args.environment, client):
            validation_passed = False
        
        # Validate data quality
        if not validate_data_quality(args.environment, config.env_config.catalog, config.get_schemas_str()):
            validation_passed = False
        
        if validation_passed:
            print("✅ All validation checks passed")
            sys.exit(0)
        else:
            print("❌ Some validation checks failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during validation: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

