#!/bin/bash

# RepairGPT Docker Setup Script
# This script helps set up the Docker environment for RepairGPT

set -e  # Exit on any error

echo "🐳 RepairGPT Docker Setup"
echo "=========================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev         Start development environment"
    echo "  prod        Start production environment"
    echo "  stop        Stop all services"
    echo "  clean       Clean up containers and volumes"
    echo "  build       Build Docker images"
    echo "  logs        Show logs"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev      # Start development environment with hot reload"
    echo "  $0 prod     # Start production environment"
    echo "  $0 logs api # Show API service logs"
}

# Function to setup environment file
setup_env() {
    if [ ! -f .env ]; then
        echo "📝 Setting up environment file..."
        cp .env.example .env
        echo "✅ Created .env file from template"
        echo "⚠️  Please edit .env file and add your API keys before proceeding"
        echo ""
        echo "Required API keys:"
        echo "  - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys"
        echo "  - ANTHROPIC_API_KEY: Get from https://console.anthropic.com/"
        echo "  - IFIXIT_API_KEY: Get from https://www.ifixit.com/api"
        echo ""
        read -p "Press Enter to continue after updating .env file..."
    fi
}

# Function to start development environment
start_dev() {
    echo "🚀 Starting development environment..."
    setup_env
    docker-compose -f docker-compose.dev.yml up --build -d
    echo ""
    echo "✅ Development environment started!"
    echo "🌐 API: http://localhost:8000"
    echo "🖥️  UI: http://localhost:8501"
    echo "📊 API Docs: http://localhost:8000/docs"
    echo ""
    echo "📝 View logs: $0 logs"
    echo "🛑 Stop services: $0 stop"
}

# Function to start production environment
start_prod() {
    echo "🚀 Starting production environment..."
    setup_env
    docker-compose up --build -d
    echo ""
    echo "✅ Production environment started!"
    echo "🌐 API: http://localhost:8000"
    echo "🖥️  UI: http://localhost:8501"
    echo ""
    echo "📝 View logs: $0 logs"
    echo "🛑 Stop services: $0 stop"
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    echo "✅ Services stopped"
}

# Function to clean up
clean_up() {
    echo "🧹 Cleaning up containers and volumes..."
    read -p "This will remove all containers and volumes. Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f docker-compose.dev.yml down -v --remove-orphans 2>/dev/null || true
        docker-compose down -v --remove-orphans 2>/dev/null || true
        docker system prune -f
        echo "✅ Cleanup completed"
    else
        echo "❌ Cleanup cancelled"
    fi
}

# Function to build images
build_images() {
    echo "🔨 Building Docker images..."
    docker-compose build --no-cache
    docker-compose -f docker-compose.dev.yml build --no-cache
    echo "✅ Images built successfully"
}

# Function to show logs
show_logs() {
    local service=$1
    if [ -n "$service" ]; then
        echo "📝 Showing logs for $service..."
        docker-compose logs -f "$service" 2>/dev/null || docker-compose -f docker-compose.dev.yml logs -f "$service"
    else
        echo "📝 Showing all logs..."
        docker-compose logs -f 2>/dev/null || docker-compose -f docker-compose.dev.yml logs -f
    fi
}

# Main script logic
case "${1:-help}" in
    "dev")
        start_dev
        ;;
    "prod")
        start_prod
        ;;
    "stop")
        stop_services
        ;;
    "clean")
        clean_up
        ;;
    "build")
        build_images
        ;;
    "logs")
        show_logs "$2"
        ;;
    "help"|*)
        show_help
        ;;
esac