#!/usr/bin/env python3
"""
Deployment Validation Script
Validates that the deployment to Databricks was successful
"""

import argparse
import sys
import subprocess
import json
import time

def validate_databricks_deployment(environment):
    """Validate Databricks deployment"""
    print(f"🔍 Validating Databricks deployment for {environment} environment...")
    
    try:
        # Check if databricks CLI is available
        result = subprocess.run(['databricks', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Databricks CLI version: {result.stdout.strip()}")
        
        # Validate bundle configuration
        result = subprocess.run(['databricks', 'bundle', 'validate', '--target', environment], 
                              capture_output=True, text=True, check=True)
        print("✅ Bundle configuration is valid")
        
        # Check if jobs exist
        result = subprocess.run(['databricks', 'jobs', 'list'], 
                              capture_output=True, text=True, check=True)
        print("✅ Successfully connected to Databricks workspace")
        
        # Check for specific jobs
        jobs_to_check = [
            'inventory_etl_job',
            'masterdata_etl_job', 
            'rail_etl_job',
            'shipping_etl_job',
            'smartalert_etl_job'
        ]
        
        for job_name in jobs_to_check:
            if job_name in result.stdout:
                print(f"✅ Job '{job_name}' found in workspace")
            else:
                print(f"⚠️  Job '{job_name}' not found in workspace")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Databricks validation failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Databricks CLI not found. Please install it first.")
        return False

def validate_sql_migrations(environment):
    """Validate SQL migrations"""
    print(f"🔍 Validating SQL migrations for {environment} environment...")
    
    try:
        # Check if Flyway is available
        result = subprocess.run(['flyway', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Flyway version: {result.stdout.strip()}")
        
        # Validate SQL files exist
        import os
        domains = ['Inventory', 'MasterData', 'Rail', 'Shipping', 'SmartAlert']
        
        for domain in domains:
            sql_dir = f"src/{domain}/sql_deployment"
            if os.path.exists(sql_dir):
                sql_files = [f for f in os.listdir(sql_dir) if f.endswith('.sql')]
                print(f"✅ {domain}: {len(sql_files)} SQL files found")
            else:
                print(f"⚠️  {domain}: SQL deployment directory not found")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Flyway validation failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Flyway not found. Please install it first.")
        return False

def main():
    parser = argparse.ArgumentParser(description='Validate Databricks deployment')
    parser.add_argument('--environment', required=True, 
                       help='Environment to validate (dev, sit, uat, prod)')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting deployment validation for {args.environment} environment")
    print("=" * 60)
    
    # Validate Databricks deployment
    databricks_valid = validate_databricks_deployment(args.environment)
    
    print("\n" + "=" * 60)
    
    # Validate SQL migrations
    sql_valid = validate_sql_migrations(args.environment)
    
    print("\n" + "=" * 60)
    
    # Overall validation result
    if databricks_valid and sql_valid:
        print("🎉 Deployment validation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Deployment validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
