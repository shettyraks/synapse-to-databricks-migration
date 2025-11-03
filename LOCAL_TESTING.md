# Local Testing Guide

This guide explains how to test SQL migrations and Databricks configurations locally before deploying to production environments.

## Prerequisites

### Required Tools
- Python 3.8+
- pip3
- Databricks CLI (optional, for bundle testing)

### Installation Commands
```bash
# Install Databricks CLI
pip install databricks-cli
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
- Execute individual test scripts

### 2. Individual Testing

#### Test SQL Migrations
```bash
# First, configure your environment
cp local.env.template local.env
# Edit local.env with your Databricks instance details

# SQL migrations are handled through Databricks notebooks/jobs
# Test by running the migration notebooks directly
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

## Test Scripts Explained

### `test-local-comprehensive.sh`
Main testing script that runs all checks:
- Prerequisites validation
- Project structure verification
- SQL file counting
- Job configuration validation
- Individual script execution


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

2. **Permission denied on scripts**
   ```bash
   chmod +x scripts/*.sh
   ```

3. **Environment variables not set**
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
   python deploy.py --environment dev
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
