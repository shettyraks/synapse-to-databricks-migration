#!/bin/bash

# Local Databricks Bundle Testing Script
# This script tests Databricks Asset Bundle configurations locally

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

echo -e "${YELLOW}Starting local Databricks Bundle testing...${NC}"

# Check if databricks CLI is installed
if ! command -v databricks &> /dev/null; then
    echo -e "${RED}✗ Databricks CLI is not installed. Please install it first.${NC}"
    echo "Install with: pip install databricks-cli"
    exit 1
fi

# Check if bundle CLI is available
if ! databricks bundle --help &> /dev/null; then
    echo -e "${RED}✗ Databricks Bundle CLI is not available. Please update your Databricks CLI.${NC}"
    exit 1
fi

# Validate bundle configuration
echo -e "${YELLOW}Validating bundle configuration...${NC}"
databricks bundle validate --target dev

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Bundle configuration is valid${NC}"
else
    echo -e "${RED}✗ Bundle configuration validation failed${NC}"
    exit 1
fi

# Test bundle deployment (dry run)
echo -e "${YELLOW}Testing bundle deployment (dry run)...${NC}"
databricks bundle deploy --target dev --dry-run

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Bundle deployment dry run successful${NC}"
else
    echo -e "${RED}✗ Bundle deployment dry run failed${NC}"
    exit 1
fi

# Test job configurations
echo -e "${YELLOW}Testing individual job configurations...${NC}"

job_files=(
    "src/Inventory/jobs/inventory_job.yml"
    "src/MasterData/jobs/masterdata_job.yml"
    "src/Rail/jobs/rail_job.yml"
    "src/Shipping/jobs/shipping_job.yml"
    "src/SmartAlert/jobs/smartalert_job.yml"
)

failed_jobs=()

for job_file in "${job_files[@]}"; do
    if [ -f "$job_file" ]; then
        echo "Validating $job_file..."
        # Basic YAML syntax check
        if python3 -c "import yaml; yaml.safe_load(open('$job_file'))" 2>/dev/null; then
            echo -e "${GREEN}✓ $job_file syntax is valid${NC}"
        else
            echo -e "${RED}✗ $job_file has invalid YAML syntax${NC}"
            failed_jobs+=("$job_file")
        fi
    else
        echo -e "${YELLOW}⚠ $job_file not found${NC}"
    fi
done

# Test notebook paths
echo -e "${YELLOW}Checking notebook paths...${NC}"
notebook_paths=(
    "src/Inventory/notebooks/inventory_etl.py"
    "src/MasterData/notebooks/masterdata_etl.py"
    "src/Rail/notebooks/rail_etl.py"
    "src/Shipping/notebooks/shipping_etl.py"
    "src/SmartAlert/notebooks/smartalert_etl.py"
)

missing_notebooks=()

for notebook in "${notebook_paths[@]}"; do
    if [ -f "$notebook" ]; then
        echo -e "${GREEN}✓ $notebook exists${NC}"
    else
        echo -e "${YELLOW}⚠ $notebook not found${NC}"
        missing_notebooks+=("$notebook")
    fi
done

# Test SQL deployment files
echo -e "${YELLOW}Checking SQL deployment files...${NC}"
domains=("Inventory" "MasterData" "Rail" "Shipping" "SmartAlert")

for domain in "${domains[@]}"; do
    sql_dir="src/${domain}/sql_deployment"
    if [ -d "$sql_dir" ]; then
        sql_count=$(find "$sql_dir" -name "*.sql" | wc -l)
        echo -e "${GREEN}✓ $domain: $sql_count SQL files found${NC}"
    else
        echo -e "${YELLOW}⚠ $domain: SQL deployment directory not found${NC}"
    fi
done

# Summary
echo -e "${YELLOW}=== Test Summary ===${NC}"

if [ ${#failed_jobs[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All job configurations are valid${NC}"
else
    echo -e "${RED}✗ Failed job configurations: ${failed_jobs[*]}${NC}"
fi

if [ ${#missing_notebooks[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All referenced notebooks exist${NC}"
else
    echo -e "${YELLOW}⚠ Missing notebooks: ${missing_notebooks[*]}${NC}"
fi

echo -e "${GREEN}🎉 Databricks Bundle testing completed!${NC}"
echo -e "${YELLOW}Note: This was a dry run. To actually deploy, run:${NC}"
echo "databricks bundle deploy --target dev"
