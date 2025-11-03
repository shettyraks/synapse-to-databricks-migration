# Synapse-to-Databricks Migration

This repository contains a complete deployment pipeline for migrating SQL Server Synapse databases to Databricks, with support for multiple environments and modular Python architecture.

## Features

- **Multi-Environment Support**: Deploy to dev, sit, uat, and prod environments
- **Modular Python Architecture**: System-independent, maintainable modules
- **SQL Migrations**: Automated schema deployment via Databricks notebooks
- **Databricks Asset Bundles**: Deploy notebooks, jobs, and configurations
- **Automated CI/CD**: GitHub Actions workflows for automated deployments
- **Comprehensive Validation**: Pre and post-deployment checks
- **Error Handling**: Robust error handling with proper cleanup

## Architecture

### Modular Design

The deployment system uses a modular Python architecture for maximum flexibility and system independence:

- **`modules/config.py`** - Configuration management
- **`modules/databricks_client.py`** - Databricks API interactions
- **`modules/deployment_orchestrator.py`** - Deployment orchestration

### Deployment Flow

1. **Configuration Validation** - Load and validate environment configuration
2. **Backup Creation** - Create database backups before migration
3. **SQL Migrations** - Run SQL migrations via Databricks notebooks/jobs
4. **Asset Deployment** - Deploy Databricks notebooks, jobs, and configurations
5. **Validation** - Verify deployment success
6. **Smoke Tests** - Run basic functionality tests

## Quick Start

### Prerequisites

- Python 3.x
- Databricks CLI installed
- GitHub access configured
- Environment variables set (see Configuration section)

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure Databricks CLI
databricks configure --token
```

### Deploy to Development

```bash
# Using main deployment script
python deploy.py --environment dev

# Or deploy with custom options
python deploy.py --environment dev --skip-validation --debug
```

### Deploy via GitHub Actions

1. Push to `develop` branch for dev deployment
2. Push to `release/sit` branch for SIT deployment
3. Push to `release/uat` branch for UAT deployment
4. Push to `main` branch for production deployment

## Configuration

### Environment Configuration

Configure environments in `config/customer_input.yml`:

```yaml
environments:
  dev:
    customer: PANDs
    catalog: rio_cicd_setup_dev
    schemas:
      - inventory
      - masterdata
```

### Environment Variables

#### Token Authentication (Default)

Set these GitHub Secrets for each environment:

- `DATABRICKS_HOST_DEV` - Databricks host URL
- `DATABRICKS_TOKEN_DEV` - Databricks API token
- `HTTP_PATH_DEV` - SQL warehouse HTTP path
- `SQL_USER_DEV` - Connection user (usually 'token')
- `SQL_PASSWORD_DEV` - Same as DATABRICKS_TOKEN_DEV

#### Service Principal Authentication (Alternative)

For Azure-based authentication, set these additional secrets:

- `SERVICE_PRINCIPAL_CLIENT_ID_DEV` - Azure AD client ID
- `SERVICE_PRINCIPAL_CLIENT_SECRET_DEV` - Azure AD client secret
- `SERVICE_PRINCIPAL_TENANT_ID_DEV` - Azure AD tenant ID

See [Authentication Guide](docs/AUTHENTICATION.md) for details.

## Usage

### Main Deployment Script

```bash
# Deploy to any environment
python deploy.py --environment <env>

# Options:
#   --skip-backup         Skip backup creation
#   --skip-migrations     Skip SQL migrations
#   --skip-validation     Skip post-deployment validation
#   --skip-smoke-tests    Skip smoke tests
#   --debug               Enable debug output
```

### Individual Scripts

```bash
# Create backup
python scripts/create_backup.py --environment dev

# Validate deployment
python scripts/validate_deployment.py --environment dev

# Run smoke tests
python scripts/run_smoke_tests.py --environment dev
```

## Module Structure

```
modules/
├── __init__.py
├── config.py                 # Configuration management
├── databricks_client.py      # Databricks API client
└── deployment_orchestrator.py  # Deployment orchestration

scripts/
├── create_backup.py          # Backup creation
├── validate_deployment.py    # Post-deployment validation
└── run_smoke_tests.py        # Smoke testing

deploy.py                     # Main deployment entry point
```

## CI/CD Workflows

### Development Deployment (`.github/workflows/cd-dev.yml`)

- Triggers on: Push to `develop` branch
- Steps:
  1. Run SQL migrations via Databricks notebooks
  2. Deploy Databricks assets
  3. Run validation

### Production Deployment (`.github/workflows/cd-prod.yml`)

- Triggers on: Push to `main` branch
- Steps:
  1. Create backup
  2. Install dependencies
  3. Run SQL migrations via Databricks notebooks
  4. Deploy Databricks assets
  5. Run validation and smoke tests

## Benefits

### System Independence

- Pure Python modules work on any OS (Linux, macOS, Windows)
- No shell script dependencies
- Easy to test and maintain

### Maintainability

- Clear separation of concerns
- Modular architecture
- Type hints throughout
- Comprehensive error handling

### Flexibility

- Customize deployment for each environment
- Skip steps as needed
- Enable debug mode for troubleshooting

## Troubleshooting

### Deployment Failures

```bash
# Run with debug output
python deploy.py --environment dev --debug

# Skip specific steps to isolate issues
python deploy.py --environment dev --skip-migrations
```

### Configuration Issues

```bash
# Validate configuration
python -c "from modules.config import ConfigManager; ConfigManager().validate()"
```

## Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit a pull request

## License

MIT
