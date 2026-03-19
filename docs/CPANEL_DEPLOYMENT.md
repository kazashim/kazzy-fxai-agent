# Kazzy Agent - cPanel Deployment Guide

## Important Considerations for cPanel Hosting

cPanel shared hosting has limitations:
- **No direct port access** - Python servers can't run on custom ports (8000, etc.)
- **Limited Python support** - Requires using cPanel's Python selector
- **No WebSocket support** - Real-time features may be limited
- **Process restrictions** - Long-running processes may be killed

## Deployment Options

### Option 1: Static Frontend + External API (Recommended)

The easiest approach is to host the frontend statically on cPanel and connect to the backend API hosted elsewhere (like a VPS, Render, Railway, etc.).

**Steps:**
1. Upload the `/dist` folder contents to `public_html` or a subdomain
2. Host the Python backend on a service that supports Python (Render, Railway, VPS)
3. Update the frontend to point to your backend URL

### Option 2: Full cPanel Python Deployment

If your cPanel supports Python applications:

**Prerequisites:**
- cPanel with Python 3.8+ support
- SSH access (required for setup)

## Step-by-Step Installation

### Step 1: Prepare Your Files

1. **Backend files** (upload to your home directory):
   - `/backend/` folder
   - Requirements.txt

2. **Frontend files** (upload to public_html):
   - All files from `/dist/`

### Step 2: Upload Backend

```bash
# Upload via File Manager or FTP
# Place in: /home/username/kazzy-backend/
```

### Step 3: Set Up Python Environment in cPanel

1. Log into cPanel
2. Navigate to **Setup Python App**
3. Create new application:
   - Python version: 3.9 or 3.10
   - Application root: `kazzy-backend`
   - Application URL: `api` (or subdomain like `api.yourdomain.com`)
   - Application startup file: `api_server.py`

4. Click **Create**
5. Note the **Virtual Environment** path provided

### Step 4: Install Dependencies

```bash
# SSH into your server
cd ~/kazzy-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 5: Configure Application

The backend will run on a specific port. cPanel's Python app feature handles this automatically.

**Important:** Update your frontend to point to your cPanel domain:
- Edit `/src/services/api.js` or similar
- Change API URL to your cPanel domain

### Step 6: Upload Frontend

1. Go to **File Manager**
2. Navigate to `public_html`
3. Upload all files from the `/dist` folder
4. Set proper permissions (755 for folders, 644 for files)

## Required Files for Upload

### Backend Requirements (requirements.txt)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
websockets==12.0
pydantic==2.5.0
ccxt==4.1.0
numpy==1.26.0
pandas==2.1.0
aiohttp==3.9.0
```

### .htaccess Configuration

Create `.htaccess` in your backend folder:

```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ api_server.py/$1 [L]
```

Or for API routing:

```apache
DirectoryIndex api_server.py
<FilesMatch \.py$>
    Options +ExecCGI
</FilesMatch>
```

## Troubleshooting cPanel Issues

### Issue: Port Already in Use

cPanel Python apps use ports dynamically. Check the assigned port in cPanel.

### Issue: Module Not Found

Ensure you're using the correct virtual environment:
```bash
source ~/kazzy-backend/venv/bin/activate
pip install -r requirements.txt
```

### Issue: 500 Internal Server Error

1. Check error logs in cPanel
2. Ensure file permissions are correct
3. Verify Python path in startup file

## Alternative: Static API Mode

If real-time trading isn't critical, you can create a simplified version that uses:

1. **Cron jobs** - Poll prices periodically
2. **AJAX calls** - Instead of WebSockets
3. **PHP backend** - Rewrite core functionality in PHP

This reduces functionality but ensures cPanel compatibility.

## Quick Start (Static Mode Only)

If you just want the dashboard without live trading:

1. Upload `/dist/*` to `public_html/`
2. Update API endpoints to point to external service
3. Done!

## Support

For cPanel-specific issues:
- Check cPanel error logs
- Contact hosting provider about Python support
- Consider upgrading to VPS if Python hosting is limited
