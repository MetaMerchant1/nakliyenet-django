#!/bin/bash
# DigitalOcean Droplet Initial Setup Script
# For Ubuntu 22.04 LTS

set -e  # Exit on error

echo "🚀 NAKLIYE NET - DigitalOcean Deployment"
echo "========================================="

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install essential packages
echo "📦 Installing essential packages..."
apt-get install -y \
    git \
    curl \
    wget \
    nano \
    ufw \
    certbot \
    python3-certbot-nginx \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Setup firewall
echo "🔥 Configuring firewall..."
ufw --force enable
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp

# Create app directory
echo "📁 Creating application directory..."
mkdir -p /opt/nakliyenet
cd /opt/nakliyenet

# Create environment file
echo "📝 Creating environment template..."
cat > .env.template << 'EOF'
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=nakliyenet.com,www.nakliyenet.com,206.81.16.220

# Database (using SQLite for now)
DATABASE_URL=sqlite:///db.sqlite3

# Firebase Credentials (Base64 encoded)
FIREBASE_CREDENTIALS_BASE64=your-base64-credentials-here

# Site URL
SITE_URL=https://nakliyenet.com
EOF

echo ""
echo "✅ Initial setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Clone your repository"
echo "2. Copy .env.template to .env and fill in values"
echo "3. Run docker-compose up -d"
echo ""
