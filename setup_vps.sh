#!/bin/bash

# Kazzy Agent - Production Deployment Script
# Run this on your VPS (DigitalOcean, Linode, AWS, etc.)

set -e

echo "====================================="
echo "  Kazzy Agent - Production Setup"
echo "====================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/kazzy-agent"
PYTHON_VERSION="3.10"
PORT=8000
DOMAIN="${DOMAIN:-your-domain.com}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Warning: Not running as root. Some features may require sudo.${NC}"
fi

# Step 1: Update system
echo -e "${GREEN}[1/7] Updating system packages...${NC}"
apt-get update -y
apt-get upgrade -y

# Step 2: Install Python and dependencies
echo -e "${GREEN}[2/7] Installing Python and dependencies...${NC}"
apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git wget curl

# Step 3: Create application directory
echo -e "${GREEN}[3/7] Creating application directory...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# Step 4: Upload/Clone application files
# If you have the files locally, upload them via SFTP first
if [ ! -f "api_server.py" ]; then
    echo -e "${YELLOW}Uploading files...${NC}"
    echo "Please upload the backend files to $APP_DIR via SFTP/FTP"
    echo "Required files:"
    echo "  - api_server.py"
    echo "  - requirements.txt"
    echo "  - kazzy_trading.py"
    echo "  - exchange_connectors.py"
    echo "  - live_feeds.py"
    echo "  - expert_advisor.py"
    echo "  - data_learning.py"
    echo "  - poe_integration.py"
    echo ""
    read -p "Press Enter when files are uploaded..."
fi

# Step 5: Create virtual environment
echo -e "${GREEN}[4/7] Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${YELLOW}requirements.txt not found. Installing basic dependencies...${NC}"
    pip install fastapi uvicorn python-dotenv websockets pydantic ccxt numpy pandas aiohttp MetaTrader5
fi

# Step 6: Create systemd service
echo -e "${GREEN}[5/7] Creating systemd service...${NC}"

cat > /etc/systemd/system/kazzy-agent.service << 'EOF'
[Unit]
Description=Kazzy Agent Trading API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/kazzy-agent
Environment="PATH=/var/www/kazzy-agent/venv/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/var/www/kazzy-agent/venv/bin/python api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 7: Configure Nginx
echo -e "${GREEN>[6/7] Configuring Nginx...${NC}"

cat > /etc/nginx/sites-available/kazzy-agent << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN_HERE;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/kazzy-agent /etc/nginx/sites-enabled/

# Test nginx config
nginx -t

# Reload nginx
systemctl reload nginx

# Step 8: Start services
echo -e "${GREEN}[7/7] Starting services...${NC}"
systemctl daemon-reload
systemctl enable kazzy-agent
systemctl start kazzy-agent
systemctl status kazzy-agent --no-pager

echo ""
echo "====================================="
echo -e "${GREEN}  Installation Complete!${NC}"
echo "====================================="
echo ""
echo "Your Kazzy Agent is now running!"
echo ""
echo "API Endpoints:"
echo "  - Main API: http://localhost:8000"
echo "  - Health: http://localhost:8000/api/health"
echo "  - Docs: http://localhost:8000/docs"
echo ""
echo "To configure HTTPS (SSL):"
echo "  certbot --nginx -d your-domain.com"
echo ""
echo "To check status:"
echo "  systemctl status kazzy-agent"
echo ""
echo "To view logs:"
echo "  journalctl -u kazzy-agent -f"
echo ""
