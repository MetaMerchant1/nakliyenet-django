# DigitalOcean Deployment Guide

## Server Information
- **IP Address:** 206.81.16.220
- **Location:** Frankfurt, Germany
- **Specs:** 1GB RAM, 1 CPU, 25GB SSD
- **OS:** Ubuntu 22.04 LTS

## Initial Setup (Run Once)

### 1. Connect to Droplet
```bash
ssh root@206.81.16.220
```

### 2. Run Setup Script
```bash
# Download and run setup
curl -o setup.sh https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/nakliyenet-django/main/deploy/digitalocean/setup.sh
chmod +x setup.sh
./setup.sh
```

Or manually:
```bash
# Clone repository
cd /opt
git clone https://github.com/YOUR_GITHUB_USERNAME/nakliyenet-django.git nakliyenet
cd nakliyenet

# Copy deployment files
cp deploy/digitalocean/docker-compose.yml .
cp deploy/digitalocean/nginx.conf .

# Create environment file
cp deploy/digitalocean/.env.template .env
nano .env  # Edit and add your credentials
```

### 3. Configure Environment Variables

Edit `.env` file:
```bash
nano /opt/nakliyenet/.env
```

Required variables:
```env
DEBUG=False
SECRET_KEY=your-django-secret-key-here
ALLOWED_HOSTS=nakliyenet.com,www.nakliyenet.com,206.81.16.220

FIREBASE_CREDENTIALS_BASE64=your-base64-encoded-credentials

SITE_URL=https://nakliyenet.com
```

To get Firebase credentials in Base64:
```bash
cat firebase-adminsdk.json | base64 -w 0
```

### 4. Start Application
```bash
cd /opt/nakliyenet
docker-compose up -d
```

### 5. Setup SSL Certificate (Let's Encrypt)

First, point your domain to the server IP (see DNS section below).

Then run:
```bash
# Stop nginx temporarily
docker-compose stop nginx

# Get certificate
certbot certonly --standalone -d nakliyenet.com -d www.nakliyenet.com --email ekremmozcan@gmail.com --agree-tos

# Copy certificates
mkdir -p /opt/nakliyenet/ssl
cp /etc/letsencrypt/live/nakliyenet.com/fullchain.pem /opt/nakliyenet/ssl/cert.pem
cp /etc/letsencrypt/live/nakliyenet.com/privkey.pem /opt/nakliyenet/ssl/key.pem

# Restart nginx
docker-compose up -d nginx
```

## DNS Configuration

Update your domain's DNS records to point to: **206.81.16.220**

### If using Cloudflare, Namecheap, or GoDaddy:

Add these A records:
```
Type: A
Name: @
Value: 206.81.16.220
TTL: Auto

Type: A
Name: www
Value: 206.81.16.220
TTL: Auto
```

Wait 5-30 minutes for DNS propagation.

## Daily Operations

### View Logs
```bash
# All logs
docker-compose logs -f

# Just web app
docker-compose logs -f web

# Just nginx
docker-compose logs -f nginx
```

### Restart Application
```bash
cd /opt/nakliyenet
docker-compose restart
```

### Update Application (Deploy New Code)
```bash
cd /opt/nakliyenet
./deploy/digitalocean/deploy.sh
```

### Check Status
```bash
docker-compose ps
```

### Access Django Shell
```bash
docker-compose exec web python manage.py shell
```

### Run Migrations
```bash
docker-compose exec web python manage.py migrate
```

### Create Superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

## Monitoring

### Check Resource Usage
```bash
# CPU and Memory
htop

# Disk usage
df -h

# Docker stats
docker stats
```

### Check Application Health
```bash
curl http://localhost:8000/
curl https://nakliyenet.com/
```

## Troubleshooting

### Application not starting?
```bash
# Check logs
docker-compose logs web

# Check if ports are in use
netstat -tulpn | grep 8000
```

### Nginx not working?
```bash
# Check config
docker-compose exec nginx nginx -t

# Reload nginx
docker-compose restart nginx
```

### Database issues?
```bash
# Backup database
cp /opt/nakliyenet/db/db.sqlite3 /opt/nakliyenet/db/db.sqlite3.backup

# Run migrations
docker-compose exec web python manage.py migrate
```

### Reset everything?
```bash
cd /opt/nakliyenet
docker-compose down -v
docker-compose up -d
```

## Security

### Firewall Status
```bash
ufw status
```

### Update System
```bash
apt update
apt upgrade -y
```

### Renew SSL Certificate (automatic, but manual if needed)
```bash
certbot renew
```

## Performance Optimization

### Enable Redis Cache (Optional)
Add to docker-compose.yml:
```yaml
  redis:
    image: redis:alpine
    restart: unless-stopped
```

### Monitor Application
```bash
# Install monitoring
docker run -d --name=netdata --pid=host --network=host \
  -v /proc:/host/proc:ro \
  -v /sys:/host/sys:ro \
  netdata/netdata
```

Access at: http://206.81.16.220:19999

## Backup Strategy

### Daily Backups
```bash
# Add to crontab
crontab -e

# Add this line (backup at 2 AM daily)
0 2 * * * cp /opt/nakliyenet/db/db.sqlite3 /opt/nakliyenet/backups/db-$(date +\%Y\%m\%d).sqlite3
```

### Manual Backup
```bash
mkdir -p /opt/nakliyenet/backups
docker-compose exec web python manage.py dumpdata > /opt/nakliyenet/backups/backup-$(date +%Y%m%d).json
```

## Cost Optimization

Current cost: **$6/month**

To upgrade if needed:
1. Go to DigitalOcean dashboard
2. Click "Resize" on your droplet
3. Select larger plan ($12 for 2GB RAM)

## Support

For issues, check:
1. Application logs: `docker-compose logs -f web`
2. Nginx logs: `docker-compose logs -f nginx`
3. System logs: `/var/log/syslog`
