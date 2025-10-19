#!/bin/bash
# Manual script to run the same checks as GitHub Actions locally
# This is useful when Docker-in-Docker isn't available in the devcontainer

set -e

echo "🔍 Running Local Development Checks"
echo "===================================="
echo "This script runs the same checks as the GitHub Actions workflow"
echo
echo "Usage: $0 [--with-integration]"
echo "  --with-integration  Include integration tests (requires real API credentials)"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    local status="$1"
    local message="$2"
    case "$status" in
        "PASS")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "FAIL")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
        "WARN")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
    esac
}

# Function to run a command and check its exit status
run_check() {
    local name="$1"
    local command="$2"

    echo -e "${BLUE}🔄 Running: $name${NC}"
    if eval "$command"; then
        print_status "PASS" "$name completed successfully"
        return 0
    else
        print_status "FAIL" "$name failed"
        return 1
    fi
}

# Track overall success
overall_success=true

echo "📋 Step 1: Environment Setup"
echo "----------------------------"

# Check Python version
python_version=$(python3 --version 2>&1)
print_status "INFO" "Python version: $python_version"

# Check if we're in the right directory
if [ -f "pyproject.toml" ] && [ -d "pysmartcocoon" ]; then
    print_status "PASS" "Working directory is correct"
else
    print_status "FAIL" "Not in the correct project directory"
    exit 1
fi

echo
echo "📋 Step 2: Python Dependencies"
echo "-------------------------------"

# Install/upgrade pip
run_check "Upgrade pip" "python3 -m pip install --upgrade pip" || overall_success=false

# Install dependencies
run_check "Install test dependencies" "pip install -r requirements_test.txt" || overall_success=false

# Install package in development mode
run_check "Install package in dev mode" "pip install -e ." || overall_success=false

echo
echo "📋 Step 3: Code Quality Checks"
echo "------------------------------"

# Run pre-commit on all files
run_check "Pre-commit hooks" "pre-commit run --all-files --color=always" || overall_success=false

# Run mypy (scoped to specific files like in the workflow)
run_check "MyPy type checking" "mypy pysmartcocoon/const.py pysmartcocoon/types.py" || overall_success=false

echo
echo "📋 Step 4: Additional Checks"
echo "----------------------------"

# Run pylint on the main package
run_check "Pylint code analysis" "pylint pysmartcocoon/ --disable=C0114,C0116" || overall_success=false

# Run black to check formatting (using same version as pre-commit)
run_check "Black formatting check" "black --check pysmartcocoon/ tests/ --line-length=79 --quiet" || overall_success=false

# Run isort to check import sorting (using same version as pre-commit)
run_check "Import sorting check" "isort --check-only pysmartcocoon/ tests/ --quiet" || overall_success=false

echo
echo "📋 Step 5: Testing"
echo "------------------"

# Run pytest (excluding integration tests by default)
if [ "$1" = "--with-integration" ]; then
    run_check "Pytest tests (including integration)" "pytest tests/ -v" || overall_success=false
else
    run_check "Pytest tests (excluding integration)" "pytest tests/ -v -k 'not integration'" || overall_success=false
fi

echo
echo "📋 Step 6: Summary"
echo "------------------"

if [ "$overall_success" = true ]; then
    print_status "PASS" "All checks passed! 🎉"
    echo
    echo "Your code is ready for commit and push to GitHub!"
    echo "The GitHub Actions workflow should pass with the same results."
    exit 0
else
    print_status "FAIL" "Some checks failed. Please fix the issues above."
    echo
    echo "Common fixes:"
    echo "  - Run 'black .' to fix formatting"
    echo "  - Run 'isort .' to fix import sorting"
    echo "  - Run 'pylint pysmartcocoon/' to see detailed linting issues"
    echo "  - Run 'mypy pysmartcocoon/const.py pysmartcocoon/types.py' for type issues"
    exit 1
fi
