#!/bin/bash

# Post-Git Testing Script
# Runs comprehensive tests after git operations to ensure everything is working

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Post-Git Testing Suite${NC}"
echo "=============================="

# Test git status
test_git_status() {
    echo -e "${YELLOW}Testing git status...${NC}"
    
    if git status --porcelain | grep -q "^??"; then
        echo -e "${YELLOW}⚠ Untracked files detected:${NC}"
        git status --porcelain | grep "^??" | sed 's/^?? /  /'
    else
        echo -e "${GREEN}✓ No untracked files${NC}"
    fi
    
    if git status --porcelain | grep -q "^ M"; then
        echo -e "${YELLOW}⚠ Modified files detected:${NC}"
        git status --porcelain | grep "^ M" | sed 's/^ M /  /'
    else
        echo -e "${GREEN}✓ No modified files${NC}"
    fi
    
    if git status --porcelain | grep -q "^A "; then
        echo -e "${GREEN}✓ Staged files ready for commit${NC}"
    fi
}

# Test file integrity
test_file_integrity() {
    echo -e "${YELLOW}Testing file integrity...${NC}"
    
    # Check critical files exist
    critical_files=(
        "databricks.yml"
        "src/Inventory/jobs/inventory_job.yml"
        "src/Inventory/sql_deployment/V1__create_inventory_header_table.sql"
        "scripts/test-simple-local-v2.sh"
        ".gitignore"
    )
    
    missing_files=0
    for file in "${critical_files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✓ $file exists${NC}"
        else
            echo -e "${RED}✗ $file missing${NC}"
            missing_files=$((missing_files + 1))
        fi
    done
    
    if [ $missing_files -eq 0 ]; then
        echo -e "${GREEN}✓ All critical files present${NC}"
    else
        echo -e "${RED}✗ $missing_files critical files missing${NC}"
        return 1
    fi
}

# Test script permissions
test_script_permissions() {
    echo -e "${YELLOW}Testing script permissions...${NC}"
    
    scripts=(
        "scripts/test-simple-local-v2.sh"
        "scripts/test-databricks-local.sh"
    )
    
    executable_scripts=0
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            if [ -x "$script" ]; then
                echo -e "${GREEN}✓ $script is executable${NC}"
                executable_scripts=$((executable_scripts + 1))
            else
                echo -e "${YELLOW}⚠ $script not executable${NC}"
            fi
        else
            echo -e "${RED}✗ $script not found${NC}"
        fi
    done
    
    echo -e "${BLUE}Executable scripts: $executable_scripts/${#scripts[@]}${NC}"
}

# Test git hooks (if any)
test_git_hooks() {
    echo -e "${YELLOW}Testing git hooks...${NC}"
    
    if [ -d ".git/hooks" ]; then
        hook_count=$(find .git/hooks -type f -executable | wc -l)
        if [ $hook_count -gt 0 ]; then
            echo -e "${GREEN}✓ $hook_count git hooks configured${NC}"
        else
            echo -e "${YELLOW}⚠ No git hooks configured${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Git hooks directory not found${NC}"
    fi
}

# Test branch information
test_branch_info() {
    echo -e "${YELLOW}Testing branch information...${NC}"
    
    current_branch=$(git branch --show-current)
    echo -e "${GREEN}✓ Current branch: $current_branch${NC}"
    
    commit_count=$(git rev-list --count HEAD)
    echo -e "${GREEN}✓ Total commits: $commit_count${NC}"
    
    last_commit=$(git log -1 --pretty=format:"%h - %s (%cr)")
    echo -e "${GREEN}✓ Last commit: $last_commit${NC}"
}

# Test remote configuration
test_remote_config() {
    echo -e "${YELLOW}Testing remote configuration...${NC}"
    
    remote_count=$(git remote | wc -l)
    if [ $remote_count -gt 0 ]; then
        echo -e "${GREEN}✓ $remote_count remote(s) configured${NC}"
        git remote -v | sed 's/^/  /'
    else
        echo -e "${YELLOW}⚠ No remote repositories configured${NC}"
        echo -e "${YELLOW}  To add a remote: git remote add origin <repository-url>${NC}"
    fi
}

# Run comprehensive tests
run_comprehensive_tests() {
    echo -e "${YELLOW}Running comprehensive tests...${NC}"
    
    if [ -f "scripts/test-simple-local-v2.sh" ]; then
        ./scripts/test-simple-local-v2.sh
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Comprehensive tests passed${NC}"
        else
            echo -e "${RED}✗ Comprehensive tests failed${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ Comprehensive test script not found${NC}"
        return 1
    fi
}

# Main execution
main() {
    echo ""
    test_git_status
    echo ""
    
    test_file_integrity
    echo ""
    
    test_script_permissions
    echo ""
    
    test_git_hooks
    echo ""
    
    test_branch_info
    echo ""
    
    test_remote_config
    echo ""
    
    run_comprehensive_tests
    echo ""
    
    echo -e "${GREEN}🎉 Post-Git testing completed!${NC}"
    echo ""
    echo -e "${BLUE}Summary:${NC}"
    echo "✓ Git repository status checked"
    echo "✓ File integrity verified"
    echo "✓ Script permissions validated"
    echo "✓ Branch and commit information displayed"
    echo "✓ Remote configuration checked"
    echo "✓ Comprehensive tests executed"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Add remote repository: git remote add origin <your-repo-url>"
    echo "2. Push to remote: git push -u origin main"
    echo "3. Set up CI/CD pipelines"
    echo "4. Configure Databricks deployment"
}

# Run main function
main
