#!/bin/bash

# Deploy SQL Migrations using Flyway
# Usage: ./scripts/deploy-sql-migrations.sh <environment>
# Trigger workflow run
# Deploy latest configuration
# Test simplified Flyway configuration

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
        CATALOG=${CATALOG_DEV:-"main"}
        ;;
    sit)
        DATABRICKS_HOST=${DATABRICKS_HOST_SIT}
        HTTP_PATH=${HTTP_PATH_SIT}
        USER=${USER_SIT}
        PASSWORD=${PASSWORD_SIT}
        SCHEMA_NAME="sit_inventory"
        CATALOG=${CATALOG_SIT:-"main"}
        ;;
    uat)
        DATABRICKS_HOST=${DATABRICKS_HOST_UAT}
        HTTP_PATH=${HTTP_PATH_UAT}
        USER=${USER_UAT}
        PASSWORD=${PASSWORD_UAT}
        SCHEMA_NAME="uat_inventory"
        CATALOG=${CATALOG_UAT:-"main"}
        ;;
    prod)
        DATABRICKS_HOST=${DATABRICKS_HOST_PROD}
        HTTP_PATH=${HTTP_PATH_PROD}
        USER=${USER_PROD}
        PASSWORD=${PASSWORD_PROD}
        SCHEMA_NAME="inventory"
        CATALOG=${CATALOG_PROD:-"main"}
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
echo "CATALOG: ${CATALOG}"

# Download Databricks JDBC driver if not present
if [ ! -f "databricks-jdbc-driver.jar" ]; then
    echo "Downloading Databricks JDBC driver..."
    curl -L -o databricks-jdbc-driver.jar "https://repo1.maven.org/maven2/com/databricks/databricks-jdbc/2.6.25/databricks-jdbc-2.6.25.jar"
    echo "Databricks JDBC driver downloaded"
fi

# Run Flyway migrations for each domain
pwd
ls -la

for domain in Inventory MasterData Rail Shipping SmartAlert; do
    echo "Deploying migrations for $domain..."
    echo "Current directory: $(pwd)"
    
    # Set domain-specific schema name
    DOMAIN_SCHEMA="${ENVIRONMENT}_$(echo $domain | tr '[:upper:]' '[:lower:]')"
    
    # Create domain-specific flyway config
    cat > flyway_${domain}.conf << FLYWAY_EOF
flyway.url=jdbc:databricks://${DATABRICKS_HOST}:443;transportMode=http;ssl=1;httpPath=${HTTP_PATH};AuthMech=3;UID=${USER};PWD=${PASSWORD};ConnCatalog=${CATALOG}
flyway.driver=com.databricks.client.jdbc.Driver
flyway.locations=filesystem:./src/$domain/sql_deployment
flyway.schemas=${DOMAIN_SCHEMA}
flyway.defaultSchema=${DOMAIN_SCHEMA}
flyway.baselineOnMigrate=true
flyway.validateOnMigrate=true
flyway.outOfOrder=false
flyway.cleanDisabled=true
FLYWAY_EOF
    
    echo "Generated Flyway config for $domain:"
    cat flyway_${domain}.conf
    
    # Debug: List all JAR files to help identify the correct one
    echo "Debug - Available JAR files:"
    find . -name "*.jar" 2>/dev/null | head -10 || echo "No JAR files found"
    
    # Find the Flyway JAR file and run it directly with Java memory flags
    # Look for the main Flyway JAR (not database-specific ones)
    echo "Debug - Searching for Flyway JAR..."
    
    # First try: Look for flyway-commandline JAR
    FLYWAY_JAR=$(find /usr/local/bin -name "flyway-commandline*.jar" 2>/dev/null | head -1)
    echo "Debug - Found in /usr/local/bin: $FLYWAY_JAR"
    
    if [ -z "$FLYWAY_JAR" ]; then
        # Second try: Look in current directory
        FLYWAY_JAR=$(find . -name "flyway-commandline*.jar" 2>/dev/null | head -1)
        echo "Debug - Found flyway-commandline JAR: $FLYWAY_JAR"
    fi
    
    if [ -z "$FLYWAY_JAR" ]; then
        # Third try: Look for main flyway JAR (not database-specific)
        echo "Debug - Looking for main flyway JAR..."
        FLYWAY_JAR=$(find . -name "flyway*.jar" 2>/dev/null | grep -v "flyway-database-" | grep -v "flyway-sql" | grep -v "flyway-core" | head -1)
        echo "Debug - Found main flyway JAR: $FLYWAY_JAR"
    fi
    
    if [ -z "$FLYWAY_JAR" ]; then
        # Fourth try: Look for any executable JAR with main class
        echo "Debug - Looking for executable JAR..."
        for jar in $(find . -name "flyway*.jar" 2>/dev/null); do
            if jar tf "$jar" 2>/dev/null | grep -q "org/flywaydb/core/Flyway.class"; then
                FLYWAY_JAR="$jar"
                echo "Debug - Found executable flyway JAR: $FLYWAY_JAR"
                break
            fi
        done
    fi
    # Set JDK Java options for native access
    export JDK_JAVA_OPTIONS="--add-opens=java.base/java.nio=ALL-UNNAMED --enable-native-access=ALL-UNNAMED"

    echo "Running Flyway migrate for $domain..."
    flyway -X -configFiles=flyway_${domain}.conf migrate
    
    
    if [ $? -eq 0 ]; then
        echo "Successfully deployed $domain migrations to $ENVIRONMENT"
        # Clean up domain-specific config file
        rm -f flyway_${domain}.conf
    else
        echo "Error deploying $domain migrations to $ENVIRONMENT"
        rm -f flyway_${domain}.conf
        exit 10
    fi
done

echo "All SQL migrations deployed successfully to $ENVIRONMENT"
