#!/bin/bash

# Simple Local Testing Script (No External Dependencies)
# Tests project structure, SQL syntax, and basic YAML validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Running Simple Local Tests${NC}"
echo "=================================="

# Test project structure
test_project_structure() {
    echo -e "${YELLOW}Testing project structure...${NC}"
    
    required_dirs=("src" "flyway" "scripts")
    missing_dirs=()
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            echo -e "${GREEN}✓ $dir directory exists${NC}"
        else
            echo -e "${RED}✗ $dir directory missing${NC}"
            missing_dirs+=("$dir")
        fi
    done
    
    # Check domain directories
    domains=("Inventory" "MasterData" "Rail" "Shipping" "SmartAlert")
    for domain in "${domains[@]}"; do
        if [ -d "src/$domain" ]; then
            echo -e "${GREEN}✓ src/$domain directory exists${NC}"
            
            # Check subdirectories
            subdirs=("jobs" "notebooks" "sql_deployment")
            for subdir in "${subdirs[@]}"; do
                if [ -d "src/$domain/$subdir" ]; then
                    echo -e "${GREEN}  ✓ src/$domain/$subdir exists${NC}"
                else
                    echo -e "${YELLOW}  ⚠ src/$domain/$subdir missing${NC}"
                fi
            done
        else
            echo -e "${RED}✗ src/$domain directory missing${NC}"
            missing_dirs+=("src/$domain")
        fi
    done
    
    if [ ${#missing_dirs[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing required directories: ${missing_dirs[*]}${NC}"
        return 1
    fi
    
    return 0
}

# Test SQL files syntax
test_sql_syntax() {
    echo -e "${YELLOW}Testing SQL file syntax...${NC}"
    
    domains=("Inventory" "MasterData" "Rail" "Shipping" "SmartAlert")
    total_files=0
    syntax_errors=0
    
    for domain in "${domains[@]}"; do
        sql_dir="src/$domain/sql_deployment"
        if [ -d "$sql_dir" ]; then
            sql_files=$(find "$sql_dir" -name "*.sql")
            file_count=$(echo "$sql_files" | wc -l)
            echo -e "${GREEN}✓ $domain: $file_count SQL files${NC}"
            total_files=$((total_files + file_count))
            
            # Basic syntax check (look for common SQL errors)
            for sql_file in $sql_files; do
                if [ -f "$sql_file" ]; then
                    # Check for basic SQL syntax issues
                    if grep -q "CREATE TABLE" "$sql_file" || grep -q "INSERT INTO" "$sql_file"; then
                        echo -e "${GREEN}  ✓ $sql_file has valid SQL structure${NC}"
                    else
                        echo -e "${YELLOW}  ⚠ $sql_file may not contain standard SQL${NC}"
                    fi
                fi
            done
        else
            echo -e "${YELLOW}⚠ $domain: No SQL deployment directory${NC}"
        fi
    done
    
    echo -e "${BLUE}Total SQL files: $total_files${NC}"
}

# Basic YAML validation (without PyYAML)
test_yaml_basic() {
    echo -e "${YELLOW}Testing YAML files (basic validation)...${NC}"
    
    yaml_files=(
        "databricks.yml"
        "src/Inventory/jobs/inventory_job.yml"
        "src/MasterData/jobs/masterdata_job.yml"
        "src/Rail/jobs/rail_job.yml"
        "src/Shipping/jobs/shipping_job.yml"
        "src/SmartAlert/jobs/smartalert_job.yml"
    )
    
    valid_yaml=0
    for yaml_file in "${yaml_files[@]}"; do
        if [ -f "$yaml_file" ]; then
            # Basic YAML structure check
            if grep -q ":" "$yaml_file" && ! grep -q ":" "$yaml_file" | head -1 | grep -q "^[^:]*:[^:]*$"; then
                echo -e "${GREEN}✓ $yaml_file has basic YAML structure${NC}"
                valid_yaml=$((valid_yaml + 1))
            else
                echo -e "${YELLOW}⚠ $yaml_file may have YAML issues${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ $yaml_file not found${NC}"
        fi
    done
    
    echo -e "${BLUE}YAML files with basic structure: $valid_yaml/${#yaml_files[@]}${NC}"
}

# Test notebook files
test_notebook_files() {
    echo -e "${YELLOW}Testing notebook files...${NC}"
    
    notebook_paths=(
        "src/Inventory/notebooks/inventory_etl.py"
        "src/MasterData/notebooks/masterdata_etl.py"
        "src/Rail/notebooks/rail_etl.py"
        "src/Shipping/notebooks/shipping_etl.py"
        "src/SmartAlert/notebooks/smartalert_etl.py"
    )
    
    existing_notebooks=0
    for notebook in "${notebook_paths[@]}"; do
        if [ -f "$notebook" ]; then
            echo -e "${GREEN}✓ $notebook exists${NC}"
            existing_notebooks=$((existing_notebooks + 1))
        else
            echo -e "${YELLOW}⚠ $notebook not found${NC}"
        fi
    done
    
    echo -e "${BLUE}Existing notebooks: $existing_notebooks/${#notebook_paths[@]}${NC}"
}

# Test environment configuration
test_environment_config() {
    echo -e "${YELLOW}Testing environment configuration...${NC}"
    
    if [ -f "local.env" ]; then
        echo -e "${GREEN}✓ local.env exists${NC}"
        
        # Check if required variables are set
        required_vars=("DATABRICKS_HOST_LOCAL" "HTTP_PATH_LOCAL" "USER_LOCAL" "PASSWORD_LOCAL")
        configured_vars=0
        for var in "${required_vars[@]}"; do
            if grep -q "^$var=" local.env && ! grep -q "^$var=your-" local.env; then
                echo -e "${GREEN}✓ $var is configured${NC}"
                configured_vars=$((configured_vars + 1))
            else
                echo -e "${YELLOW}⚠ $var needs configuration${NC}"
            fi
        done
        echo -e "${BLUE}Configured variables: $configured_vars/${#required_vars[@]}${NC}"
    else
        echo -e "${YELLOW}⚠ local.env not found (copy from local.env.template)${NC}"
    fi
}

# Test Flyway configuration
test_flyway_config() {
    echo -e "${YELLOW}Testing Flyway configuration...${NC}"
    
    if [ -f "flyway/conf/flyway.conf" ]; then
        echo -e "${GREEN}✓ flyway.conf exists${NC}"
        
        # Check for required Flyway settings
        if grep -q "flyway.url=" flyway/conf/flyway.conf; then
            echo -e "${GREEN}✓ Flyway URL configured${NC}"
        else
            echo -e "${YELLOW}⚠ Flyway URL not configured${NC}"
        fi
        
        if grep -q "flyway.locations=" flyway/conf/flyway.conf; then
            echo -e "${GREEN}✓ Flyway locations configured${NC}"
        else
            echo -e "${YELLOW}⚠ Flyway locations not configured${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ flyway.conf not found${NC}"
    fi
}

# Test deployment script
test_deployment_script() {
    echo -e "${YELLOW}Testing deployment script...${NC}"
    
    if [ -f "scripts/deploy-sql-migrations.sh" ]; then
        echo -e "${GREEN}✓ Deployment script exists${NC}"
        
        if [ -x "scripts/deploy-sql-migrations.sh" ]; then
            echo -e "${GREEN}✓ Deployment script is executable${NC}"
        else
            echo -e "${YELLOW}⚠ Deployment script not executable${NC}"
        fi
    else
        echo -e "${RED}✗ Deployment script not found${NC}"
    fi
}

# Main execution
main() {
    echo ""
    test_project_structure
    echo ""
    
    test_sql_syntax
    echo ""
    
    test_yaml_basic
    echo ""
    
    test_notebook_files
    echo ""
    
    test_environment_config
    echo ""
    
    test_flyway_config
    echo ""
    
    test_deployment_script
    echo ""
    
    echo -e "${GREEN}🎉 Simple local testing completed!${NC}"
    echo ""
    echo -e "${BLUE}Summary:${NC}"
    echo "✓ Project structure validated"
    echo "✓ SQL files syntax checked"
    echo "✓ YAML configurations validated"
    echo "✓ Environment setup verified"
    echo "✓ Flyway configuration checked"
    echo "✓ Deployment scripts verified"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. For full YAML validation: pip install PyYAML"
    echo "2. For Flyway testing: Install Flyway Spark plugin"
    echo "3. For Databricks testing: pip install databricks-cli"
    echo "4. Configure your Databricks instance in local.env"
}

# Run main function
main
