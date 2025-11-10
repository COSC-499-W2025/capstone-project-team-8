#!/bin/bash

# Ollama Model Setup Script
# This script helps you pull and manage Ollama models in the Docker container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker Compose is running
check_services() {
    if ! docker compose ps | grep -q "ollama"; then
        print_error "Ollama service is not running. Please start it first:"
        echo "docker compose up -d"
        exit 1
    fi
    print_status "Ollama service is running"
}

# Pull a model
pull_model() {
    local model=$1
    print_status "Pulling model: $model"
    docker compose exec ollama ollama pull "$model"
    print_status "Model $model pulled successfully"
}

# List available models
list_models() {
    print_status "Available models in Ollama:"
    docker compose exec ollama ollama list
}

# Show running models
show_running() {
    print_status "Currently running models:"
    docker compose exec ollama ollama ps
}

# Test model
test_model() {
    local model=$1
    print_status "Testing model: $model"
    docker compose exec ollama ollama run "$model" "Hello, respond with just 'OK' if you're working"
}

# Show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [MODEL]"
    echo ""
    echo "Commands:"
    echo "  pull <model>     Pull a specific model (e.g., llama3.1:8b, mistral)"
    echo "  list             List all downloaded models"
    echo "  running          Show currently running models"
    echo "  test <model>     Test a specific model"
    echo "  setup            Pull recommended models for development"
    echo "  help             Show this help message"
    echo ""
    echo "Popular models:"
    echo "  llama3.1:8b      - Good balance of performance and size"
    echo "  mistral          - Fast and efficient"
    echo "  codellama        - Optimized for code generation"
    echo "  llama3.2:3b      - Smaller, faster model"
}

# Setup recommended models
setup_models() {
    print_status "Setting up recommended models..."
    print_warning "This will download several GB of data. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        pull_model "llama3.2:3b"   # Smaller model first
        pull_model "mistral"       # Fast model
        pull_model "llama3.1:8b"   # Main model
        print_status "Model setup complete!"
    else
        print_status "Setup cancelled"
    fi
}

# Main script
case "${1:-help}" in
    "pull")
        if [ -z "$2" ]; then
            print_error "Please specify a model name"
            echo "Example: $0 pull llama3.1:8b"
            exit 1
        fi
        check_services
        pull_model "$2"
        ;;
    "list")
        check_services
        list_models
        ;;
    "running")
        check_services
        show_running
        ;;
    "test")
        if [ -z "$2" ]; then
            print_error "Please specify a model name"
            echo "Example: $0 test llama3.1:8b"
            exit 1
        fi
        check_services
        test_model "$2"
        ;;
    "setup")
        check_services
        setup_models
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac