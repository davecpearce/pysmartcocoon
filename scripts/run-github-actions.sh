#!/bin/bash
# Helper script to run GitHub Actions locally using act

set -e

echo "🚀 GitHub Actions Local Runner"
echo "================================"
echo

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "❌ act is not installed. Please rebuild your devcontainer."
    echo "   The devcontainer should include act automatically."
    exit 1
fi

# Check if Docker is available
if ! docker info &> /dev/null; then
    echo "❌ Docker is not available. Please ensure Docker is running."
    echo "   Note: You may need to run this in a container with Docker-in-Docker support."
    exit 1
fi

echo "✅ act and Docker are available"
echo

# Show available workflows
echo "📋 Available workflows:"
ls -la .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null | awk '{print "   " $9}' | sed 's/.github\/workflows\///g'
echo

# Function to run a specific workflow
run_workflow() {
    local workflow_name="$1"
    echo "🔄 Running workflow: $workflow_name"
    echo "   Command: act -W .github/workflows/$workflow_name"
    echo "   (This may take a few minutes to download Docker images on first run)"
    echo

    act -W ".github/workflows/$workflow_name" --verbose
}

# Function to list available workflows
list_workflows() {
    echo "📋 Available workflows:"
    for workflow in .github/workflows/*.yml .github/workflows/*.yaml; do
        if [ -f "$workflow" ]; then
            workflow_name=$(basename "$workflow")
            echo "   - $workflow_name"
        fi
    done
}

# Main script logic
case "${1:-help}" in
    "tests"|"test")
        run_workflow "tests.yaml"
        ;;
    "lint"|"linting")
        run_workflow "tests.yaml"
        ;;
    "list"|"ls")
        list_workflows
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  tests, test    Run the tests workflow (linting, pre-commit, mypy)"
        echo "  lint, linting  Same as tests"
        echo "  list, ls       List available workflows"
        echo "  help, -h       Show this help message"
        echo
        echo "Examples:"
        echo "  $0 tests       # Run the tests workflow"
        echo "  $0 list        # List all workflows"
        echo
        echo "Note: First run may take longer as Docker images are downloaded."
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Run '$0 help' for usage information."
        exit 1
        ;;
esac
