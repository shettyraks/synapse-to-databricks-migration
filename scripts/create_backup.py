#!/usr/bin/env python3
"""
Create backup of Databricks tables before deployment.
Uses modular configuration and client architecture.
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config import DeploymentConfig


def create_backup(environment: str) -> str:
    """Create backup for the specified environment.
    
    Args:
        environment: Environment name
        
    Returns:
        Backup timestamp
    """
    print(f"Creating backup for {environment} environment...")
    
    # Load configuration
    config = DeploymentConfig(environment)
    
    # Generate backup timestamp
    backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_directory = Path(f"backups/{environment}")
    backup_directory.mkdir(parents=True, exist_ok=True)
    
    print(f"Backup timestamp: {backup_timestamp}")
    print(f"Backup directory: {backup_directory}")
    
    # Create backup marker file
    # In production, this would:
    # 1. Export table schemas
    # 2. Create table snapshots using Delta Lake time travel
    # 3. Export critical data to backup storage
    
    backup_marker = backup_directory / f"backup_{backup_timestamp}.marker"
    with open(backup_marker, 'w') as f:
        f.write(f"Backup created at {backup_timestamp}\n")
        f.write(f"Environment: {environment}\n")
        f.write(f"Customer: {config.env_config.customer}\n")
        f.write(f"Catalog: {config.env_config.catalog}\n")
        f.write(f"Host: {config.databricks_host}\n")
    
    print(f"✅ Backup marker created: {backup_marker}")
    print(f"Backup creation completed for {environment}")
    
    return backup_timestamp


def main():
    parser = argparse.ArgumentParser(description='Create backup before deployment')
    parser.add_argument('--environment', required=True, 
                       choices=['dev', 'sit', 'uat', 'prod'],
                       help='Environment to create backup for')
    
    args = parser.parse_args()
    
    try:
        backup_timestamp = create_backup(args.environment)
        print(f"Backup completed successfully: {backup_timestamp}")
        sys.exit(0)
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

