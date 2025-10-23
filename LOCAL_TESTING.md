# Local Testing Guide

This guide explains how to test Flyway and Databricks configurations locally before deploying to production environments.

## Prerequisites

### Required Tools
- Docker and Docker Compose
- Python 3.8+
- pip3
- Databricks CLI (optional, for bundle testing)

### Installation Commands
```bash
# Install Databricks CLI
pip install databricks-cli

# Install Flyway (if not using Docker)
# Download from: https://flywaydb.org/download/
```

## Quick Start

### 1. Run Comprehensive Tests
```bash
./scripts/test-local-comprehensive.sh
```

This script will:
- Check prerequisites
- Validate project structure
- Test SQL files
- Test job configurations
- Run Docker-based tests
- Execute individual test scripts

### 2. Individual Testing

#### Test Flyway Migrations
```bash
# First, configure your environment
cp local.env.template local.env
# Edit local.env with your Databricks instance details

# Run Flyway tests
./scripts/test-flyway-local.sh
```

#### Test Databricks Bundle
```bash
./scripts/test-databricks-local.sh
```

## Configuration

### Environment Setup
1. Copy the template file:
   ```bash
   cp local.env.template local.env
   ```

2. Edit `local.env` with your Databricks instance details:
   ```bash
   DATABRICKS_HOST_LOCAL=your-instance.cloud.databricks.com
   HTTP_PATH_LOCAL=/sql/1.0/warehouses/your-warehouse-id
   USER_LOCAL=your-username@company.com
   PASSWORD_LOCAL=your-password-or-token
   ```

### Docker Testing
For testing without a Databricks instance:
```bash
docker-compose -f docker-compose.local.yml up -d
```

This starts:
- Spark SQL server (port 10000)
- Flyway container
- Jupyter notebook (port 8888)

## Test Scripts Explained

### `test-local-comprehensive.sh`
Main testing script that runs all checks:
- Prerequisites validation
- Project structure verification
- SQL file counting
- Job configuration validation
- Docker service testing
- Individual script execution

### `test-flyway-local.sh`
Tests Flyway migrations:
- Creates domain-specific configurations
- Validates SQL syntax
- Tests Flyway info and validate commands
- Reports success/failure for each domain

### `test-databricks-local.sh`
Tests Databricks Asset Bundle:
- Validates bundle configuration
- Tests dry-run deployment
- Validates job YAML files
- Checks notebook paths
- Reports missing components

## Project Structure Validation

The tests verify this structure:
```
src/
├── Inventory/
│   ├── jobs/inventory_job.yml
│   ├── notebooks/inventory_etl.py
│   └── sql_deployment/
│       ├── V1__create_inventory_header_table.sql
│       ├── V2__create_inventory_transaction_table.sql
│       └── ...
├── MasterData/
├── Rail/
├── Shipping/
└── SmartAlert/
```

## Troubleshooting

### Common Issues

1. **Missing Databricks CLI**
   ```bash
   pip install databricks-cli
   ```

2. **Docker not running**
   ```bash
   sudo systemctl start docker  # Linux
   # or start Docker Desktop
   ```

3. **Permission denied on scripts**
   ```bash
   chmod +x scripts/*.sh
   ```

4. **Environment variables not set**
   - Ensure `local.env` exists and is properly configured
   - Check that all required variables are set

### Debug Mode
Run scripts with debug output:
```bash
bash -x ./scripts/test-local-comprehensive.sh
```

## Next Steps

After successful local testing:

1. **Deploy to Development**
   ```bash
   ./scripts/deploy-sql-migrations.sh dev
   ```

2. **Deploy Databricks Bundle**
   ```bash
   databricks bundle deploy --target dev
   ```

3. **Run Integration Tests**
   - Test actual data processing
   - Validate job execution
   - Check data quality

## Support

For issues or questions:
1. Check the script output for specific error messages
2. Verify your Databricks instance configuration
3. Ensure all required files and directories exist
4. Review the troubleshooting section above
