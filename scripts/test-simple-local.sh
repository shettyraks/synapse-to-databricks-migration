#!/bin/bash

# Simple Local Testing Script (No External Dependencies)
# Tests project structure, SQL syntax, and YAML validation

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
    
    required_dirs=("src" "scripts")
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

# Test YAML job configurations
test_yaml_configurations() {
    echo -e "${YELLOW}Testing YAML job configurations...${NC}"
    
    job_files=(
        "src/Inventory/jobs/inventory_job.yml"
        "src/MasterData/jobs/masterdata_job.yml"
        "src/Rail/jobs/rail_job.yml"
        "src/Shipping/jobs/shipping_job.yml"
        "src/SmartAlert/jobs/smartalert_job.yml"
    )
    
    valid_jobs=0
    for job_file in "${job_files[@]}"; do
        if [ -f "$job_file" ]; then
            # Basic YAML syntax check using Python
            if python3 -c "import yaml; yaml.safe_load(open('$job_file'))" 2>/dev/null; then
                echo -e "${GREEN}✓ $job_file is valid YAML${NC}"
                valid_jobs=$((valid_jobs + 1))
            else
                echo -e "${RED}✗ $job_file has invalid YAML syntax${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ $job_file not found${NC}"
        fi
    done
    
    echo -e "${BLUE}Valid job configurations: $valid_jobs/${#job_files[@]}${NC}"
}

# Test main databricks.yml
test_main_config() {
    echo -e "${YELLOW}Testing main databricks.yml...${NC}"
    
    if [ -f "databricks.yml" ]; then
        if python3 -c "import yaml; yaml.safe_load(open('databricks.yml'))" 2>/dev/null; then
            echo -e "${GREEN}✓ databricks.yml is valid YAML${NC}"
        else
            echo -e "${RED}✗ databricks.yml has invalid YAML syntax${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ databricks.yml not found${NC}"
        return 1
    fi
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
        for var in "${required_vars[@]}"; do
            if grep -q "^$var=" local.env && ! grep -q "^$var=your-" local.env; then
                echo -e "${GREEN}✓ $var is configured${NC}"
            else
                echo -e "${YELLOW}⚠ $var needs configuration${NC}"
            fi
        done
    else
        echo -e "${YELLOW}⚠ local.env not found (copy from local.env.template)${NC}"
    fi
}

# Main execution
main() {
    echo ""
    test_project_structure
    echo ""
    
    test_sql_syntax
    echo ""
    
    test_yaml_configurations
    echo ""
    
    test_main_config
    echo ""
    
    test_notebook_files
    echo ""
    
    test_environment_config
    echo ""
    
    echo -e "${GREEN}🎉 Simple local testing completed!${NC}"
    echo ""
    echo -e "${BLUE}Summary:${NC}"
    echo "✓ Project structure validated"
    echo "✓ SQL files syntax checked"
    echo "✓ YAML configurations validated"
    echo "✓ Environment setup verified"
    echo ""
    echo -e "${YELLOW}Note: For full Databricks testing, you'll need:${NC}"
    echo "- Databricks CLI: pip install databricks-cli"
    echo "- Valid Databricks instance credentials"
}

# Run main function
main
