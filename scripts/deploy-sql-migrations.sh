#!/bin/bash

# Deploy SQL Migrations using Flyway
# Usage: ./scripts/deploy-sql-migrations.sh <environment>

set -e

ENVIRONMENT=$1
if [ -z "$ENVIRONMENT" ]; then
    echo "Error: Environment parameter is required"
    echo "Usage: $0 <environment>"
    exit 1
fi

echo "Deploying SQL migrations to $ENVIRONMENT environment..."

# Set environment-specific variables
case $ENVIRONMENT in
    dev)
        DATABRICKS_HOST=${DATABRICKS_HOST_DEV}
        HTTP_PATH=${HTTP_PATH_DEV}
        USER=${USER_DEV}
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

# Create environment-specific flyway config
cat > flyway.conf << FLYWAY_EOF
flyway.url=jdbc:spark://${DATABRICKS_HOST}:443/default;transportMode=http;ssl=1;httpPath=${HTTP_PATH};AuthMech=3;UID=${USER};PWD=${PASSWORD}
flyway.user=${USER}
flyway.password=${PASSWORD}
flyway.locations=filesystem:sql_deployment
flyway.schemas=${SCHEMA_NAME}
flyway.defaultSchema=${SCHEMA_NAME}
flyway.baselineOnMigrate=true
flyway.validateOnMigrate=true
flyway.outOfOrder=false
flyway.cleanDisabled=true
FLYWAY_EOF

# Run Flyway migrations for each domain
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
