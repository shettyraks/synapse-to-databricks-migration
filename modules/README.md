# Modules

This directory contains the core modules for the synapse-to-databricks migration deployment system.

## Architecture

The deployment system uses a modular approach for system independence and maintainability:

### Core Modules

1. **`config.py`** - Configuration Management
   - Loads and validates environment-specific configuration
   - Manages Databricks credentials
   - Provides `DeploymentConfig` and `ConfigManager` classes

2. **`databricks_client.py`** - Databricks API Client
   - Wraps Databricks CLI commands
   - Manages bundle deployments
   - Handles job operations (list, get, run)

3. **`flyway_runner.py`** - Flyway Migration Runner
   - Downloads Flyway and JDBC driver if needed
   - Creates Flyway configuration dynamically
   - Runs SQL migrations
   - Validates migration state

4. **`deployment_orchestrator.py`** - Deployment Orchestration
   - Manages the complete deployment lifecycle
   - Coordinates backup, migrations, asset deployment, validation, and smoke tests
   - Provides flexible deployment options

## Usage

### Main Deployment Script

```bash
# Deploy to development
python deploy.py --environment dev

# Deploy to production with all safety checks
python deploy.py --environment prod

# Deploy with custom options
python deploy.py --environment sit --skip-validation --debug
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

## Benefits of Modular Approach

1. **System Independence**: Works on any system with Python 3.x
2. **Maintainability**: Clear separation of concerns
3. **Testability**: Each module can be tested independently
4. **Flexibility**: Easy to extend with new features
5. **Error Handling**: Comprehensive error handling with proper exceptions
6. **Type Safety**: Type hints throughout

## Configuration

Configuration is managed through:
- `config/customer_input.yml` - Environment-specific settings
- Environment variables - Credentials and connection details

## Adding New Modules

To add a new module:

1. Create `modules/new_module.py`
2. Implement your functionality with type hints
3. Import and use in `deployment_orchestrator.py`
4. Update this README

