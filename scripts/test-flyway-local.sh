#!/bin/bash

# Local Flyway Testing Script
# This script tests Flyway migrations locally against a Databricks instance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f "local.env" ]; then
    source local.env
    echo -e "${GREEN}✓ Loaded local environment configuration${NC}"
else
    echo -e "${RED}✗ local.env file not found. Please copy local.env.template to local.env and configure it.${NC}"
    exit 1
fi

# Validate required environment variables
required_vars=("DATABRICKS_HOST_LOCAL" "HTTP_PATH_LOCAL" "USER_LOCAL" "PASSWORD_LOCAL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}✗ Required environment variable $var is not set${NC}"
        exit 1
    fi
done

echo -e "${YELLOW}Starting local Flyway testing...${NC}"
echo "Target Databricks Host: $DATABRICKS_HOST_LOCAL"
echo "Schema Prefix: $LOCAL_SCHEMA_PREFIX"

# Create local flyway configuration
create_flyway_config() {
    local domain=$1
    local schema_name="${LOCAL_SCHEMA_PREFIX}$(echo $domain | tr '[:upper:]' '[:lower:]')"
    
    cat > "flyway_local_$(echo $domain | tr '[:upper:]' '[:lower:]').conf" << FLYWAY_EOF
# Local Flyway Configuration for $domain
flyway.url=jdbc:databricks://${DATABRICKS_HOST_LOCAL}:443/default;transportMode=http;ssl=1;httpPath=${HTTP_PATH_LOCAL};AuthMech=3;UID=${USER_LOCAL};PWD=${PASSWORD_LOCAL};ConnCatalog=main
flyway.driver=com.databricks.client.jdbc.Driver
flyway.locations=filesystem:src/${domain}/sql_deployment
flyway.schemas=${schema_name}
flyway.defaultSchema=${schema_name}
flyway.baselineOnMigrate=true
flyway.validateOnMigrate=true
flyway.outOfOrder=false
flyway.cleanDisabled=true
flyway.loggers=slf4j
FLYWAY_EOF
}

# Test Flyway for a specific domain
test_domain_migrations() {
    local domain=$1
    local schema_name="${LOCAL_SCHEMA_PREFIX}$(echo $domain | tr '[:upper:]' '[:lower:]')"
    
    echo -e "${YELLOW}Testing $domain migrations...${NC}"
    
    # Create domain-specific flyway config
    create_flyway_config "$domain"
    
    # Check if SQL files exist
    if [ ! -d "src/${domain}/sql_deployment" ]; then
        echo -e "${RED}✗ SQL deployment directory not found for $domain${NC}"
        return 1
    fi
    
    # Count SQL files
    sql_count=$(find "src/${domain}/sql_deployment" -name "*.sql" | wc -l)
    echo "Found $sql_count SQL migration files"
    
    if [ "$sql_count" -eq 0 ]; then
        echo -e "${YELLOW}⚠ No SQL files found for $domain, skipping...${NC}"
        return 0
    fi
    
    # Set JDK Java options for native access
    export JDK_JAVA_OPTIONS="--enable-native-access=ALL-UNNAMED"
    
    # Test Flyway info
    echo "Running Flyway info for $domain..."
    flyway -configFiles="flyway_local_$(echo $domain | tr '[:upper:]' '[:lower:]').conf" info
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flyway info successful for $domain${NC}"
    else
        echo -e "${RED}✗ Flyway info failed for $domain${NC}"
        return 1
    fi
    
    # Test Flyway validate (dry run)
    echo "Running Flyway validate for $domain..."
    flyway -configFiles="flyway_local_$(echo $domain | tr '[:upper:]' '[:lower:]').conf" validate
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flyway validate successful for $domain${NC}"
    else
        echo -e "${RED}✗ Flyway validate failed for $domain${NC}"
        return 1
    fi
    
    # Clean up config file
    rm "flyway_local_$(echo $domain | tr '[:upper:]' '[:lower:]').conf"
    
    return 0
}

# Main execution
echo -e "${YELLOW}Testing Flyway migrations for all domains...${NC}"

domains=("Inventory" "MasterData" "Rail" "Shipping" "SmartAlert")
failed_domains=()

for domain in "${domains[@]}"; do
    if test_domain_migrations "$domain"; then
        echo -e "${GREEN}✓ $domain migrations test passed${NC}"
    else
        echo -e "${RED}✗ $domain migrations test failed${NC}"
        failed_domains+=("$domain")
    fi
    echo "---"
done

# Summary
if [ ${#failed_domains[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 All Flyway migration tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some migration tests failed: ${failed_domains[*]}${NC}"
    exit 1
fi
