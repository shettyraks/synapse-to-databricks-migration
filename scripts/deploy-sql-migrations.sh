#!/bin/bash

# Deploy SQL Migrations using Flyway
# Usage: ./scripts/deploy-sql-migrations.sh <environment>
# Trigger workflow run

set -e

ENVIRONMENT=$1
if [ -z "$ENVIRONMENT" ]; then
    echo "Error: Environment parameter is required"
    echo "Usage: $0 <environment>"
    exit 1
fi

echo "Deploying SQL migrations to $ENVIRONMENT environment..."

# Debug: Print environment variables
echo "Debug - Environment variables:"
echo "DATABRICKS_HOST_DEV: ${DATABRICKS_HOST}"
echo "HTTP_PATH_DEV: ${HTTP_PATH_DEV}"
echo "USER_DEV: ${USER_DEV}"
echo "PASSWORD_DEV: ${PASSWORD_DEV:0:10}..." # Show first 10 chars only

# Set environment-specific variables
case $ENVIRONMENT in
    dev)
        DATABRICKS_HOST=${DATABRICKS_HOST}
        HTTP_PATH=${HTTP_PATH_DEV:-"/sql/1.0/warehouses/8b5728cafe72b647"}
        USER=${USER_DEV:-"token"}
        PASSWORD=${PASSWORD_DEV}
        SCHEMA_NAME="dev_inventory"
        ;;
    sit)
        DATABRICKS_HOST=${DATABRICKS_HOST_SIT}
        HTTP_PATH=${HTTP_PATH_SIT}
        USER=${USER_SIT}
        PASSWORD=${PASSWORD_SIT}
        SCHEMA_NAME="sit_inventory"
        ;;
    uat)
        DATABRICKS_HOST=${DATABRICKS_HOST_UAT}
        HTTP_PATH=${HTTP_PATH_UAT}
        USER=${USER_UAT}
        PASSWORD=${PASSWORD_UAT}
        SCHEMA_NAME="uat_inventory"
        ;;
    prod)
        DATABRICKS_HOST=${DATABRICKS_HOST_PROD}
        HTTP_PATH=${HTTP_PATH_PROD}
        USER=${USER_PROD}
        PASSWORD=${PASSWORD_PROD}
        SCHEMA_NAME="inventory"
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
echo "SCHEMA_NAME: ${SCHEMA_NAME}"

# Download Databricks JDBC driver if not present
if [ ! -f "databricks-jdbc-driver.jar" ]; then
    echo "Downloading Databricks JDBC driver..."
    curl -L -o databricks-jdbc-driver.jar "https://repo1.maven.org/maven2/com/databricks/databricks-jdbc/2.6.25/databricks-jdbc-2.6.25.jar"
    echo "Databricks JDBC driver downloaded"
fi


cat > flyway.conf << FLYWAY_EOF
flyway.url=jdbc:databricks://adb-3243176766981043.3.azuredatabricks.net:443;transportMode=http;ssl=1;httpPath=${HTTP_PATH};AuthMech=3;UID=token;PWD=${PASSWORD};ConnCatalog=main
flyway.driver=com.databricks.client.jdbc.Driver
flyway.user=token
flyway.password=${PASSWORD}
flyway.locations=filesystem:sql_deployment
flyway.schemas=${SCHEMA_NAME}
flyway.defaultSchema=${SCHEMA_NAME}
flyway.baselineOnMigrate=true
flyway.validateOnMigrate=true
flyway.outOfOrder=false
flyway.cleanDisabled=true
FLYWAY_EOF

# Debug: Print the generated flyway.conf
echo "Debug - Generated flyway.conf:"
cat flyway.conf

# Run Flyway migrations for each domain
pwd
ls -la

for domain in Inventory MasterData Rail Shipping SmartAlert; do
    echo "Deploying migrations for $domain..."
    cd src/$domain/sql_deployment    
    # Run Flyway migrate
    flyway -configFiles=../../../flyway.conf migrate
    
    if [ $? -eq 0 ]; then
        echo "Successfully deployed $domain migrations to $ENVIRONMENT"
    else
        echo "Error deploying $domain migrations to $ENVIRONMENT"
        exit 1
    fi
    
    cd ../../..
done

echo "All SQL migrations deployed successfully to $ENVIRONMENT"
