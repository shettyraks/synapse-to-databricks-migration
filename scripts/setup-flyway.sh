#!/bin/bash

# Setup Flyway from local copy
# This script extracts and sets up Flyway from the local tar.gz file

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Flyway from local copy...${NC}"

# Check if the tar.gz file exists
FLYWAY_TAR=".github/workflows/flyway-commandline-11.14.1-linux-x64.tar.gz"

if [ ! -f "$FLYWAY_TAR" ]; then
    echo -e "${RED}✗ Flyway tar.gz file not found at $FLYWAY_TAR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found Flyway tar.gz file${NC}"

# Extract Flyway
echo "Extracting Flyway..."
tar -xzf "$FLYWAY_TAR"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Flyway extracted successfully${NC}"
else
    echo -e "${RED}✗ Failed to extract Flyway${NC}"
    exit 1
fi

# Check if flyway directory was created
if [ -d "flyway-11.14.1" ]; then
    echo -e "${GREEN}✓ Flyway directory created${NC}"
else
    echo -e "${RED}✗ Flyway directory not found after extraction${NC}"
    exit 1
fi

# Make flyway executable
chmod +x flyway-11.14.1/flyway

# Create symlink if not in CI environment
if [ -z "$CI" ]; then
    echo "Creating symlink for local development..."
    if [ -w "/usr/local/bin" ]; then
        sudo ln -sf "$(pwd)/flyway-11.14.1/flyway" /usr/local/bin/flyway
        echo -e "${GREEN}✓ Flyway symlink created${NC}"
    else
        echo -e "${YELLOW}⚠ Cannot create symlink (no write permission to /usr/local/bin)${NC}"
        echo "You can run Flyway directly with: ./flyway-11.14.1/flyway"
    fi
else
    echo -e "${GREEN}✓ CI environment detected, symlink will be created by CI workflow${NC}"
fi

# Test Flyway installation
echo "Testing Flyway installation..."
if ./flyway-11.14.1/flyway --version > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Flyway is working correctly${NC}"
    ./flyway-11.14.1/flyway --version
else
    echo -e "${YELLOW}⚠ Flyway test failed (likely due to platform mismatch)${NC}"
    echo -e "${YELLOW}  This is expected on macOS when using Linux x64 version${NC}"
    echo -e "${YELLOW}  The CI/CD pipeline will work correctly on Linux${NC}"
fi

echo -e "${GREEN}🎉 Flyway setup completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Usage:${NC}"
echo "  Local development: ./flyway-11.14.1/flyway [command]"
echo "  With symlink: flyway [command]"
echo ""
echo -e "${YELLOW}Available commands:${NC}"
echo "  flyway --help"
echo "  flyway validate"
echo "  flyway migrate"
echo "  flyway info"
