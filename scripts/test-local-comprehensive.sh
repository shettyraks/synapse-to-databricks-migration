#!/bin/bash

# Comprehensive Local Testing Script
# Tests both Flyway and Databricks configurations locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting comprehensive local testing for Synapse to Databricks migration${NC}"
echo "=================================================="

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check if required tools are installed
    tools=("docker" "docker-compose" "python3" "pip3")
    missing_tools=()
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            echo -e "${GREEN}✓ $tool is installed${NC}"
        else
            echo -e "${RED}✗ $tool is not installed${NC}"
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing required tools: ${missing_tools[*]}${NC}"
        echo "Please install the missing tools and try again."
        exit 1
    fi
    
    # Check if Flyway is installed
    if command -v flyway &> /dev/null; then
        echo -e "${GREEN}✓ Flyway is installed${NC}"
    else
        echo -e "${YELLOW}⚠ Flyway is not installed. Installing via Docker...${NC}"
    fi
    
    # Check if Databricks CLI is installed
    if command -v databricks &> /dev/null; then
        echo -e "${GREEN}✓ Databricks CLI is installed${NC}"
    else
        echo -e "${YELLOW}⚠ Databricks CLI is not installed${NC}"
        echo "Install with: pip install databricks-cli"
    fi
}

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

# Test SQL files
test_sql_files() {
    echo -e "${YELLOW}Testing SQL migration files...${NC}"
    
    domains=("Inventory" "MasterData" "Rail" "Shipping" "SmartAlert")
    total_files=0
    total_domains=0
    
    for domain in "${domains[@]}"; do
        sql_dir="src/$domain/sql_deployment"
        if [ -d "$sql_dir" ]; then
            sql_files=$(find "$sql_dir" -name "*.sql" | wc -l)
            echo -e "${GREEN}✓ $domain: $sql_files SQL files${NC}"
            total_files=$((total_files + sql_files))
            total_domains=$((total_domains + 1))
        else
            echo -e "${YELLOW}⚠ $domain: No SQL deployment directory${NC}"
        fi
    done
    
    echo -e "${BLUE}Total: $total_files SQL files across $total_domains domains${NC}"
}

# Test job configurations
test_job_configurations() {
    echo -e "${YELLOW}Testing job configurations...${NC}"
    
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
            if python3 -c "import yaml; yaml.safe_load(open('$job_file'))" 2>/dev/null; then
                echo -e "${GREEN}✓ $job_file is valid YAML${NC}"
                valid_jobs=$((valid_jobs + 1))
            else
                echo -e "${RED}✗ $job_file has invalid YAML${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ $job_file not found${NC}"
        fi
    done
    
    echo -e "${BLUE}Valid job configurations: $valid_jobs/${#job_files[@]}${NC}"
}

# Test with Docker Compose (if available)
test_with_docker() {
    echo -e "${YELLOW}Testing with Docker Compose...${NC}"
    
    if [ -f "docker-compose.local.yml" ]; then
        echo -e "${GREEN}✓ Docker Compose file found${NC}"
        
        # Start services
        echo "Starting local services..."
        docker-compose -f docker-compose.local.yml up -d
        
        # Wait for services to be ready
        echo "Waiting for services to be ready..."
        sleep 10
        
        # Test Spark SQL connection
        if docker exec local-spark-sql /opt/bitnami/spark/bin/spark-sql --version &> /dev/null; then
            echo -e "${GREEN}✓ Spark SQL is running${NC}"
        else
            echo -e "${RED}✗ Spark SQL is not responding${NC}"
        fi
        
        # Test Flyway
        if docker exec local-flyway flyway --version &> /dev/null; then
            echo -e "${GREEN}✓ Flyway is running${NC}"
        else
            echo -e "${RED}✗ Flyway is not responding${NC}"
        fi
        
        # Stop services
        echo "Stopping services..."
        docker-compose -f docker-compose.local.yml down
        
    else
        echo -e "${YELLOW}⚠ Docker Compose file not found${NC}"
    fi
}

# Run individual test scripts
run_test_scripts() {
    echo -e "${YELLOW}Running individual test scripts...${NC}"
    
    # Test Flyway
    if [ -f "scripts/test-flyway-local.sh" ]; then
        echo "Running Flyway tests..."
        chmod +x scripts/test-flyway-local.sh
        if ./scripts/test-flyway-local.sh; then
            echo -e "${GREEN}✓ Flyway tests passed${NC}"
        else
            echo -e "${RED}✗ Flyway tests failed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Flyway test script not found${NC}"
    fi
    
    # Test Databricks Bundle
    if [ -f "scripts/test-databricks-local.sh" ]; then
        echo "Running Databricks Bundle tests..."
        chmod +x scripts/test-databricks-local.sh
        if ./scripts/test-databricks-local.sh; then
            echo -e "${GREEN}✓ Databricks Bundle tests passed${NC}"
        else
            echo -e "${RED}✗ Databricks Bundle tests failed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Databricks Bundle test script not found${NC}"
    fi
}

# Main execution
main() {
    check_prerequisites
    echo ""
    
    test_project_structure
    echo ""
    
    test_sql_files
    echo ""
    
    test_job_configurations
    echo ""
    
    test_with_docker
    echo ""
    
    run_test_scripts
    echo ""
    
    echo -e "${GREEN}🎉 Comprehensive local testing completed!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Copy local.env.template to local.env and configure your Databricks instance"
    echo "2. Run: ./scripts/test-flyway-local.sh"
    echo "3. Run: ./scripts/test-databricks-local.sh"
    echo "4. For Docker testing: docker-compose -f docker-compose.local.yml up"
}

# Run main function
main
