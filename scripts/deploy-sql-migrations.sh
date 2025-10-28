#!/bin/bash

# Deploy SQL Migrations using Flyway
# Usage: ./scripts/deploy-sql-migrations.sh <environment> [customer]
# Trigger workflow run
# Deploy latest configuration
# Test simplified Flyway configuration

set -e

ENVIRONMENT=$1
if [ -z "$ENVIRONMENT" ]; then
    echo "Error: Environment parameter is required"
    echo "Usage: $0 <environment> [customer]"
    exit 1
fi

# Load config-driven values (customer, catalog, schemas)
CONFIG_PATH=${CONFIG_PATH:-"config/customer_input.yml"}
echo "Loading config from ${CONFIG_PATH} for environment ${ENVIRONMENT}"
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Error: Config file not found at ${CONFIG_PATH}"
    exit 2
fi

# Ensure Python deps (PyYAML) are available in CI; assume local dev has them
if ! python3 -c 'import yaml' >/dev/null 2>&1; then
    echo "PyYAML not found; trying to install locally (pip --user)" || true
    python3 -m pip install --user -q PyYAML || true
fi

eval "$(python3 scripts/read_config.py ${CONFIG_PATH} ${ENVIRONMENT})"

# Allow overriding CUSTOMER via arg/env
CUSTOMER=${2:-${CUSTOMER}}
if [ -z "$CUSTOMER" ]; then
    echo "Error: CUSTOMER not resolved from config or args"
    exit 3
fi

echo "Deploying SQL migrations to $ENVIRONMENT environment..."

# Debug: Print environment variables
echo "Debug - Environment variables:"
echo "DATABRICKS_HOST_DEV: ${DATABRICKS_HOST}"
echo "HTTP_PATH_DEV: ${HTTP_PATH_DEV}"
echo "USER_DEV: ${USER_DEV}"
echo "PASSWORD_DEV: ${PASSWORD_DEV:0:10}..." # Show first 10 chars only
echo "Customer: ${CUSTOMER}"

# Set environment-specific variables
case $ENVIRONMENT in
    dev)
        DATABRICKS_HOST=${DATABRICKS_HOST}
        HTTP_PATH=${HTTP_PATH_DEV}
        USER=${USER_DEV:-"token"}
        PASSWORD=${PASSWORD_DEV}
        SCHEMA_Names=${SCHEMAS}
        CATALOG=${CATALOG:-"main"}
        ;;
    sit)
        DATABRICKS_HOST=${DATABRICKS_HOST_SIT}
        HTTP_PATH=${HTTP_PATH_SIT}
        USER=${USER_SIT}
        PASSWORD=${PASSWORD_SIT}
        SCHEMA_Names=${SCHEMAS}
        CATALOG=${CATALOG:-"main"}
        ;;
    uat)
        DATABRICKS_HOST=${DATABRICKS_HOST_UAT}
        HTTP_PATH=${HTTP_PATH_UAT}
        USER=${USER_UAT}
        PASSWORD=${PASSWORD_UAT}
        SCHEMA_NAME=${SCHEMAS}
        CATALOG=${CATALOG:-"main"}
        ;;
    prod)
        DATABRICKS_HOST=${DATABRICKS_HOST_PROD}
        HTTP_PATH=${HTTP_PATH_PROD}
        USER=${USER_PROD}
        PASSWORD=${PASSWORD_PROD}
        SCHEMA_NAME=${SCHEMAS}
        CATALOG=${CATALOG:-"main"}
        ;;
    *)
        echo "Error: Unknown environment $ENVIRONMENT"
    exit 1
    ;;
esac

# Debug: Print final values after fallback
echo "Debug - Final values after fallback:"
echo "DATABRICKS_HOST: ${DATABRICKS_HOST}"
echo "HTTP_PATH: ${HTTP_PATH}"
echo "USER: ${USER}"
echo "PASSWORD: ${PASSWORD:0:10}..."
echo "SCHEMAS: ${SCHEMAS}"
echo "CATALOG: ${CATALOG}"
echo "CUSTOMER: ${CUSTOMER}"

# Download Databricks JDBC driver if not present
if [ ! -f "databricks-jdbc-driver.jar" ]; then
    echo "Downloading Databricks JDBC driver..."
    curl -L -o databricks-jdbc-driver.jar "https://repo1.maven.org/maven2/com/databricks/databricks-jdbc/2.6.25/databricks-jdbc-2.6.25.jar"
    echo "Databricks JDBC driver downloaded"
fi

# Build flyway.locations from all src/*/sql_deployment directories
FLYWAY_LOCATIONS=$(find ./src -type d -path "./src/*/sql_deployment" | sed 's#^#filesystem:#' | paste -sd, -)
if [ -z "$FLYWAY_LOCATIONS" ]; then
    echo "Warning: No sql_deployment directories found under ./src"
fi
echo "FLYWAY_LOCATIONS: $FLYWAY_LOCATIONS"
#DATABRICKS_HOST="adb-3243176766981043.3.azuredatabricks.net"
cat > flyway.conf << FLYWAY_EOF
flyway.url=jdbc:databricks://${DATABRICKS_HOST}:443;transportMode=http;ssl=1;httpPath=${HTTP_PATH};AuthMech=3;UID=${USER};PWD=${PASSWORD};ConnCatalog=${CATALOG}
flyway.driver=com.databricks.client.jdbc.Driver
flyway.locations=${FLYWAY_LOCATIONS}
flyway.schemas=${SCHEMAS}
flyway.defaultSchema=flyway_${CATALOG}
flyway.baselineOnMigrate=true
flyway.validateOnMigrate=true
flyway.outOfOrder=false
flyway.cleanDisabled=true
flyway.placeholders.customer=${CUSTOMER}
FLYWAY_EOF

# Debug: Print the generated flyway.conf
echo "Debug - Generated flyway.conf:"
cat flyway.conf

# Run Flyway migrations
pwd
ls -la

echo "Running Flyway migrate for all domains..."
echo "Current directory: $(pwd)"
echo "Flyway locations: ${FLYWAY_LOCATIONS}"
# Set JDK Java options for native access
export JDK_JAVA_OPTIONS="--add-opens=java.base/java.nio=ALL-UNNAMED --enable-native-access=ALL-UNNAMED"

echo "Running Flyway repair (update checksums)..."
flyway -configFiles=flyway.conf repair

echo "Running Flyway migrate..."
flyway -X -configFiles=flyway.conf migrate

if [ $? -eq 0 ]; then
    echo "Successfully deployed all migrations to $ENVIRONMENT"
else
    echo "Error deploying migrations to $ENVIRONMENT"
    exit 10
fi

echo "All SQL migrations deployed successfully to $ENVIRONMENT"
