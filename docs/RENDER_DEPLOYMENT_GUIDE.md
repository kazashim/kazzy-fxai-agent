# Deploy Kazzy Agent on Render.com

This guide walks you through deploying Kazzy Agent (frontend + backend) on Render.com.

## Prerequisites

- GitHub account
- Render.com account (free tier available)
- API keys for exchanges (optional, for live trading)

## Architecture Overview

Render.com offers two deployment options:
1. **Static Site (Frontend)** - Free tier available
2. **Web Service (Backend)** - Free tier with 750 hours/month

## Option 1: Deploy Frontend Only (Static Site)

### Step 1: Build the Frontend

```bash
cd /workspace/kazzy-agent
npm install
npm run build
```

This creates a `dist/` folder with your static frontend.

### Step 2: Connect to GitHub

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New +** > **Static Site**

### Step 3: Configure Static Site

| Setting | Value |
|---------|-------|
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |
| **Node Version** | `18` |

### Step 4: Environment Variables

Add these in Render dashboard:

```env
VITE_API_URL=https://your-backend.onrender.com
VITE_APP_NAME=Kazzy Agent
```

### Step 5: Deploy

Click **Create Static Site** and wait for deployment.

---

## Option 2: Deploy Full Stack (Frontend + Backend)

### Step 1: Create Backend Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** > **Web Service**

### Step 2: Configure Backend

| Setting | Value |
|---------|-------|
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3.11` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn api_server:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

### Step 3: Environment Variables

Add these in the Environment section:

```env
# API Keys (optional - for live trading)
BINANCE_API_KEY=your_binance_key
BINANCE_API_SECRET=your_binance_secret
BYBIT_API_KEY=your_bybit_key
BYBIT_API_SECRET=your_bybit_secret
COINBASE_API_KEY=your_coinbase_key
COINBASE_API_SECRET=your_coinbase_secret

# AI Provider (optional)
OPENAI_API_KEY=your_openai_key
POE_API_KEY=your_poe_key

# Security
SECRET_KEY=your_random_secret_key_here
ENCRYPTION_KEY=your_32_char_encryption_key

# Trading Settings
MAX_DAILY_LOSS=5
MAX_POSITION_SIZE=2
DEFAULT_RISK_PERCENT=1
```

### Step 4: Create render.yaml (Recommended)

Create `render.yaml` in your project root for automatic deployment:

```yaml
# render.yaml
services:
  # Backend Web Service
  - type: web
    name: kazzy-backend
    region: oregon
    plan: free
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api_server:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: BINANCE_API_KEY
        sync: false
      - key: BINANCE_API_SECRET
        sync: false
      - key: OPENAI_API_KEY
        sync: false

  # Frontend Static Site
  - type: web
    name: kazzy-frontend
    plan: free
    rootDir: dist
    buildCommand: echo "No build needed for static site"
    staticPublishPath: .
    headers:
      - path: /*
        name: Cache-Control
        value: public, max-age=0, must-revalidate
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    envVars:
      - key: VITE_API_URL
        fromService:
          type: web
          name: kazzy-backend
          envVarKey: RENDER_EXTERNAL_URL
```

### Step 5: Deploy

1. Push to GitHub
2. Render will auto-detect `render.yaml` and deploy both services

---

## Backend Requirements

Create `backend/requirements.txt`:

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
ccxt==4.2.27
python-dotenv==1.0.0
aiohttp==3.9.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
cryptography==41.0.7
websockets==12.0
pydantic==2.5.3
pydantic-settings==2.1.0
MetaTrader5==5.0.45
```

## Free Tier Limitations

| Resource | Free Tier Limit |
|----------|-----------------|
| **Web Service** | 750 hours/month |
| **Static Site** | Unlimited |
| **Disk** | 512 MB |
| **Memory** | 512 MB |
| **Sleep After** | 15 minutes inactivity |

## Troubleshooting

### CORS Errors
Make sure your backend has CORS configured:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Rate Limits
- CoinGecko: 10-30 calls/minute (free tier)
- Exchange APIs: Check specific limits

### Keep Backend Awake
Use Render's cron jobs or a free uptime service to prevent cold starts.

---

## Connecting Custom Domain

1. Go to your Static Site settings
2. Click **Custom Domains**
3. Add your domain (e.g., `kazzy.yoursite.com`)
4. Update DNS records as shown

---

## Security Best Practices

1. **Never commit API keys** - Use Render environment variables
2. **Enable HTTPS** - Render provides SSL automatically
3. **Use secrets** - Enable disk encryption for sensitive data
4. **Rate limiting** - Implement in your FastAPI backend

## Support

- Render Docs: https://render.com/docs
- Kazzy Agent Issues: https://github.com/your-repo/issues
