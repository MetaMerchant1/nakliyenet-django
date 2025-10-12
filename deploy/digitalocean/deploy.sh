#!/bin/bash
# Deployment Script for DigitalOcean
# Run this on the droplet to deploy/update the application

set -e

echo "🚀 Deploying NAKLIYE NET..."

# Navigate to app directory
cd /opt/nakliyenet

# Pull latest changes from GitHub
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Build and restart containers
echo "🐳 Building and restarting containers..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T web python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Show container status
echo ""
echo "✅ Deployment completed!"
echo ""
docker-compose ps

echo ""
echo "📋 To view logs:"
echo "   docker-compose logs -f web"
echo ""
echo "📋 To restart:"
echo "   docker-compose restart"
echo ""
