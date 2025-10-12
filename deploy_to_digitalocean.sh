#!/bin/bash
# Automated DigitalOcean Docker Deployment Script
# Run this on DigitalOcean droplet: bash <(curl -s https://raw.githubusercontent.com/MetaMerchant1/nakliyenet-django/main/deploy_to_digitalocean.sh)

set -e

echo "🚀 Starting DigitalOcean Docker Deployment for nakliyenet.com"
echo "============================================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Install Docker
echo -e "${BLUE}📦 Step 1/10: Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

# Step 2: Install Docker Compose
echo -e "${BLUE}📦 Step 2/10: Installing Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    apt-get update
    apt-get install -y docker-compose-plugin
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

# Step 3: Clone Repository
echo -e "${BLUE}📥 Step 3/10: Cloning repository...${NC}"
cd /opt
if [ -d "nakliyenet" ]; then
    echo "Repository exists, pulling latest changes..."
    cd nakliyenet
    git pull origin main
else
    git clone https://github.com/MetaMerchant1/nakliyenet-django.git nakliyenet
    cd nakliyenet
fi
echo -e "${GREEN}✅ Repository ready${NC}"

# Step 4: Create .env file
echo -e "${BLUE}⚙️  Step 4/10: Creating environment file...${NC}"
cat > deploy/digitalocean/.env << 'EOF'
# PRODUCTION ENVIRONMENT
SECRET_KEY=django-insecure-CHANGE-THIS-nakliyenet-prod-2025
DEBUG=False
ALLOWED_HOSTS=nakliyenet.com,www.nakliyenet.com,206.81.16.220
ACCOUNT_DEFAULT_HTTP_PROTOCOL=https

# Database (PostgreSQL with Docker)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=nakliyenet
DB_USER=nakliyenet_user
DB_PASSWORD=postgres_secure_password_2025
DB_HOST=db
DB_PORT=5432

# Site URLs
SITE_URL=https://nakliyenet.com
IOS_APP_URL=https://apps.apple.com/app/nakliyenet
ANDROID_APP_URL=https://play.google.com/store/apps/details?id=com.nakliyenet.app

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=748357954203-eecqdmkgmv6n4qklhehod760ok2622d9.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=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

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
SECURE_HSTS_SECONDS=31536000

# Email (Console for now)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@nakliyenet.com
EOF
echo -e "${GREEN}✅ Environment configured${NC}"

# Step 5: Start Docker Containers
echo -e "${BLUE}🐳 Step 5/10: Starting Docker containers...${NC}"
cd deploy/digitalocean
docker compose down 2>/dev/null || true
docker compose up -d
echo -e "${GREEN}✅ Containers started${NC}"

# Step 6: Wait for PostgreSQL
echo -e "${BLUE}⏳ Step 6/10: Waiting for PostgreSQL to be ready...${NC}"
sleep 20
echo -e "${GREEN}✅ PostgreSQL ready${NC}"

# Step 7: Run Migrations
echo -e "${BLUE}📊 Step 7/10: Running database migrations...${NC}"
docker compose exec -T web python manage.py migrate --noinput
echo -e "${GREEN}✅ Migrations completed${NC}"

# Step 8: Collect Static Files
echo -e "${BLUE}📦 Step 8/10: Collecting static files...${NC}"
docker compose exec -T web python manage.py collectstatic --noinput
echo -e "${GREEN}✅ Static files collected${NC}"

# Step 9: Create Superuser
echo -e "${BLUE}👤 Step 9/10: Creating superuser...${NC}"
docker compose exec -T web python manage.py shell << 'PYTHON_EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@nakliyenet.com', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
PYTHON_EOF
echo -e "${GREEN}✅ Superuser ready${NC}"

# Step 10: Configure Django Site and OAuth
echo -e "${BLUE}⚙️  Step 10/10: Configuring Django Site and OAuth...${NC}"
docker compose exec -T web python manage.py shell << 'PYTHON_EOF'
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Update Site
site = Site.objects.get(pk=1)
site.domain = 'nakliyenet.com'
site.name = 'Nakliyenet'
site.save()
print(f'✓ Site configured: {site.domain}')

# Configure Google OAuth
app, created = SocialApp.objects.get_or_create(
    provider='google',
    defaults={
        'name': 'Google OAuth',
        'client_id': '748357954203-eecqdmkgmv6n4qklhehod760ok2622d9.apps.googleusercontent.com',
        'secret': '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',
    }
)

if not created:
    app.client_id = '748357954203-eecqdmkgmv6n4qklhehod760ok2622d9.apps.googleusercontent.com'
    app.secret = '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'
    app.save()

app.sites.add(site)
print(f'✓ Google OAuth configured')
PYTHON_EOF
echo -e "${GREEN}✅ Django configured${NC}"

# Show Status
echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${BLUE}📋 Container Status:${NC}"
docker compose ps
echo ""
echo -e "${BLUE}🌐 Access URLs:${NC}"
echo "   Website:    http://206.81.16.220"
echo "   Admin:      http://206.81.16.220/admin/"
echo "   Credentials: admin / admin123"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "   1. Test the website at http://206.81.16.220"
echo "   2. Setup SSL with: certbot certonly --standalone -d nakliyenet.com -d www.nakliyenet.com"
echo "   3. Change admin password at /admin/"
echo ""
echo -e "${BLUE}🔍 Useful Commands:${NC}"
echo "   View logs:    cd /opt/nakliyenet/deploy/digitalocean && docker compose logs -f"
echo "   Restart:      cd /opt/nakliyenet/deploy/digitalocean && docker compose restart"
echo "   Stop:         cd /opt/nakliyenet/deploy/digitalocean && docker compose down"
echo "   Update code:  cd /opt/nakliyenet && git pull && cd deploy/digitalocean && docker compose restart"
echo ""
