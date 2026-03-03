#!/bin/bash

# Social Connect Deployment Script
# This script helps deploy the application to different platforms

set -e

echo "🚀 Social Connect Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Setup environment variables
setup_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before continuing."
        print_warning "Important: Set secure passwords and API keys!"
        read -p "Press Enter after editing .env file..."
    else
        print_success ".env file found"
    fi
}

# Local deployment with Docker
deploy_local() {
    echo "🏠 Starting local deployment..."
    
    check_docker
    setup_env
    
    # Stop existing containers
    docker-compose down
    
    # Build and start services
    docker-compose up --build -d
    
    print_success "Application deployed locally!"
    echo "🌐 Frontend: http://localhost"
    echo "🔧 Backend API: http://localhost:8003"
    echo "📊 Health Check: http://localhost:8003/api/v1/health"
}

# Production deployment preparation
prepare_production() {
    echo "🏭 Preparing for production deployment..."
    
    # Update constants.py for production
    sed -i.bak 's/DEV_MODE = True/DEV_MODE = False/' backend/constants.py
    sed -i.bak 's/API_HOST = "localhost"/API_HOST = "0.0.0.0"/' backend/constants.py
    
    # Build frontend for production
    cd src
    npm run build
    cd ..
    
    print_success "Production build completed"
}

# Deploy to Render.com
deploy_render() {
    echo "☁️  Deploying to Render.com..."
    
    prepare_production
    
    # Check if Render CLI is installed
    if ! command -v render &> /dev/null; then
        print_warning "Render CLI not found. Please install it first:"
        echo "npm install -g @render/cli"
        exit 1
    fi
    
    # Deploy using render.yaml
    render deploy
    
    print_success "Deployed to Render.com!"
    echo "🌐 Your app will be available at: https://your-app-name.onrender.com"
}

# Deploy to DigitalOcean
deploy_digitalocean() {
    echo "🌊 Deploying to DigitalOcean..."
    
    prepare_production
    
    # Create DigitalOcean droplet (requires doctl)
    if ! command -v doctl &> /dev/null; then
        print_warning "DigitalOcean CLI not found. Please install it first."
        exit 1
    fi
    
    # This is a simplified deployment - you'd need to configure more
    echo "Please manually deploy to DigitalOcean using the Docker setup:"
    echo "1. Create a droplet with Docker installed"
    echo "2. Copy your code to the droplet"
    echo "3. Run: docker-compose up -d"
    
    print_success "DigitalOcean deployment instructions provided"
}

# Deploy to AWS
deploy_aws() {
    echo "☁️  Deploying to AWS..."
    
    prepare_production
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_warning "AWS CLI not found. Please install it first."
        exit 1
    fi
    
    echo "AWS deployment requires additional setup:"
    echo "1. Create ECS cluster"
    echo "2. Push Docker image to ECR"
    echo "3. Create task definition"
    echo "4. Set up load balancer"
    
    print_success "AWS deployment instructions provided"
}

# SSL certificate generation
generate_ssl() {
    echo "🔒 Generating SSL certificate..."
    
    if ! command -v certbot &> /dev/null; then
        print_warning "Certbot not found. Please install it first."
        exit 1
    fi
    
    # Create ssl directory
    mkdir -p ssl
    
    # Generate certificate (requires domain and email)
    read -p "Enter your domain name: " DOMAIN
    read -p "Enter your email: " EMAIL
    
    certbot certonly --standalone -d $DOMAIN --email $EMAIL --agree-tos --non-interactive
    
    # Copy certificates to ssl directory
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ./ssl/cert.pem
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ./ssl/key.pem
    
    print_success "SSL certificate generated for $DOMAIN"
}

# Database backup
backup_database() {
    echo "💾 Creating database backup..."
    
    check_docker
    
    # Backup MongoDB
    docker exec social-connect-mongodb mongodump --out /backup/$(date +%Y%m%d_%H%M%S)
    
    print_success "Database backup completed"
}

# Show logs
show_logs() {
    echo "📋 Showing application logs..."
    
    check_docker
    
    docker-compose logs -f
}

# Main menu
main() {
    echo "Choose deployment option:"
    echo "1) Local deployment (Docker)"
    echo "2) Deploy to Render.com"
    echo "3) Deploy to DigitalOcean"
    echo "4) Deploy to AWS"
    echo "5) Generate SSL certificate"
    echo "6) Backup database"
    echo "7) Show logs"
    echo "8) Exit"
    
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1)
            deploy_local
            ;;
        2)
            deploy_render
            ;;
        3)
            deploy_digitalocean
            ;;
        4)
            deploy_aws
            ;;
        5)
            generate_ssl
            ;;
        6)
            backup_database
            ;;
        7)
            show_logs
            ;;
        8)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            main
            ;;
    esac
}

# Run main function
main
