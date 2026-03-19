# Kazzy Agent - Complete Setup & API Integration Guide

## Your AI-Powered Universal Trading Assistant

**Version 2.0 | March 2026**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Platform API Setup](#platform-api-setup)
   - [Binance API](#binance-api)
   - [Bybit API](#bybit-api)
   - [Coinbase API](#coinbase-api)
   - [MetaTrader 4/5](#metatrader-45)
   - [cTrader](#ctrader)
   - [Interactive Brokers](#interactive-brokers)
   - [Alpaca](#alpaca)
3. [AI Configuration](#ai-configuration)
4. [Trading Commands](#trading-commands)
5. [Auto-Trading Setup](#auto-trading-setup)
6. [Risk Management](#risk-management)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Trading account(s) with supported platforms

### Initial Setup Steps

1. **Access the Application**
   - Navigate to the deployed URL
   - The dashboard will display with all platform connectors

2. **Connect Your Exchanges**
   - Go to Settings tab
   - Select your trading platform
   - Enter your API credentials
   - Click Connect

3. **Configure AI**
   - Choose AI provider (Poe or OpenAI)
   - Enter your API key
   - Select preferred AI model

4. **Enable Auto-Trading**
   - Toggle Auto-Trading switch
   - Configure risk parameters
   - Select trading strategies

---

## Platform API Setup

### Binance API

Binance is the world's largest cryptocurrency exchange, offering spot trading, futures, and margin.

#### How to Get Binance API Key

1. **Log into Binance**
   - Visit [binance.com](https://www.binance.com)
   - Click "Login" and enter credentials
   - Complete 2FA verification

2. **Navigate to API Management**
   - Click your profile icon (top right)
   - Select "API Management" from dropdown

3. **Create New API Key**
   - Click "Create API"
   - Select "System generated"
   - Enter a label (e.g., "Kazzy Agent")
   - Complete security verification

4. **Configure Permissions**
   - ✅ Enable "Enable Spot & Margin Trading"
   - ✅ Enable "Enable Futures"
   - ❌ Disable "Enable Withdrawals" (security)
   - ❌ Disable "Enable Internal Transfer"

5. **Save Your Credentials**
   - API Key: `your_api_key_here`
   - Secret Key: `your_secret_key_here`

#### Important Security Notes

- Never share your API secret with anyone
- Enable IP restriction if possible
- Use trade-only permissions
- Regularly rotate your API keys

---

### Bybit API

Bybit is a popular derivatives exchange offering USDT perpetual, inverse contracts, and spot trading.

#### How to Get Bybit API Key

1. **Log into Bybit**
   - Visit [bybit.com](https://www.bybit.com)
   - Click "Login" top right
   - Complete identity verification

2. **Access API Settings**
   - Hover over your avatar
   - Click "API"
   - Or visit: Settings → API

3. **Create API Key**
   - Click "Create New Key"
   - Select key type: "API Key"
   - Enter a name: "Kazzy Agent"
   - Select permissions:
     - ✅ Trade (required)
     - ✅ Order (required)
     - ❌ Read-only (not sufficient)
     - ❌ Withdraw (disable)

4. **Download Credentials**
   - API Key: `xxxxxxxxxx`
   - Secret Key: `xxxxxxxxxx`
   - **Important**: Save immediately, secret shown only once

#### Connection Settings

| Parameter | Value |
|-----------|-------|
| Exchange ID | `bybit` |
| Testnet Available | Yes |
| Max Leverage | 100x |
| Supported Assets | USDT Perp, Inverse, Spot |

---

### Coinbase API

Coinbase is a regulated US-based cryptocurrency exchange with strong security compliance.

#### How to Get Coinbase API Key

1. **Log into Coinbase**
   - Visit [coinbase.com](https://www.coinbase.com)
   - Complete identity verification (KYC)

2. **Navigate to API**
   - Click your name (top right)
   - Select "Settings"
   - Click "API" tab

3. **Create API Key**
   - Click "+ New API Key"
   - Select permissions:
     - ✅ View accounts
     - ✅ Trade
     - ✅ Convert
     - ❌ Transfer (disable)
   - Add your IP addresses (optional but recommended)

4. **Save Credentials**
   - API Key
   - Secret Key
   - Passphrase (if shown)

#### API Permissions Required

| Permission | Required | Purpose |
|------------|----------|---------|
| View Accounts | Yes | Check balances |
| Trade | Yes | Execute trades |
| Convert | Yes | Swap assets |
| Transfer | No | Security |

---

### MetaTrader 4/5

MetaTrader is the industry standard for forex and CFD trading, featuring Expert Advisors (EAs).

#### MT5 Setup (Recommended)

1. **Download MetaTrader 5**
   - Download from your broker's website
   - Or from [metatrader5.com](https://www.metatrader5.com)

2. **Install and Login**
   - Install the application
   - Open MT5
   - File → Login to Trade Account
   - Enter your account credentials

3. **Enable DLL Imports**
   - Tools → Options
   - Go to "Expert Advisors" tab
   - ✅ Allow DLL imports
   - ✅ Allow external experts

4. **Install Kazzy EA**
   - Open File → Open Data Folder
   - Navigate to MQL5 → Experts
   - Copy Kazzy EA file here
   - Restart MT5
   - Drag EA onto chart

5. **Configure EA Settings**
   - Input your API credentials
   - Set trading parameters
   - Enable "Allow live trading"

#### MT4 Setup (Alternative)

1. **Download MetaTrader 4**
   - Get from your broker
   - Install and login

2. **Enable Trading**
   - Tools → Options
   - Expert Advisors tab:
     - ✅ Allow automated trading
     - ✅ Allow DLL imports

3. **Install Expert Advisor**
   - File → Open Data Folder
   - MQL4 → Experts
   - Copy EA file
   - Restart MT4

#### MetaTrader Connection Details

| Platform | Protocol | Port | Features |
|----------|----------|------|----------|
| MT5 | WebSocket | 443 | Full trading, EAs |
| MT4 | WebSocket | 443 | Full trading, EAs |

---

### cTrader

cTrader is a professional forex and CFD trading platform by Spotware.

#### How to Get cTrader API Access

1. **Download cTrader**
   - Get from [spotware.com](https://www.spotware.com/ctrader)
   - Or from your broker

2. **Create cTrader ID**
   - Sign up at [spotware.com](https://www.spotware.com)
   - Verify your account

3. **Enable API Access**
   - Open cTrader
   - Go to Tools → cTrader ID
   - Login with your credentials
   - Enable "Allow algorithmic trading"

4. **Get Connection Details**
   - Broker ID: Your broker's ID
   - Account: Your trading account number
   - Password: Your trading password

#### cTrader Features

| Feature | Available |
|---------|-----------|
| Spot FX | Yes |
| CFDs | Yes |
| Market Orders | Yes |
| Pending Orders | Yes |
| Stop Loss/Take Profit | Yes |
| Expert Advisors | Yes (cBots) |

---

### Interactive Brokers

Interactive Brokers (IBKR) offers global trading across stocks, options, futures, forex, and commodities.

#### How to Get IBKR API Key

1. **Open IBKR Account**
   - Visit [interactivebrokers.com](https://www.interactivebrokers.com)
   - Complete account opening
   - Fund your account

2. **Configure API Access**
   - Log into Client Portal
   - Settings → API Settings
   - Click "Create API Key"
   - Enter a name: "Kazzy Agent"

3. **Set Permissions**
   - ✅ Market Data (required)
   - ✅ Trade (required)
   - ✅ Portfolio (required)
   - ❌ Account Management (optional)

4. **Save Credentials**
   - API Key ID
   - API Key Secret
   - Trading Account Number

#### Connection Parameters

| Parameter | Value |
|-----------|-------|
| Gateway | `interactivebrokers` |
| Port | 4002 (paper) / 4001 (live) |
| Market Data | Real-time |
| Assets | Stocks, Options, Futures, Forex |

---

### Alpaca

Alpaca is a commission-free stock trading API, perfect for US equities.

#### How to Get Alpaca API Key

1. **Sign Up**
   - Visit [alpaca.markets](https://alpaca.markets)
   - Click "Get Started"
   - Complete verification

2. **Generate API Keys**
   - Log into Dashboard
   - Go to "Paper Trading" or "Live Trading"
   - Click "Generate API Key"
   - **Important**: Save both Key ID and Secret

3. **Enable Trading**
   - For paper trading: Use test keys
   - For live trading: Request approval

#### Alpaca Configuration

| Parameter | Value |
|-----------|-------|
| Endpoint (Paper) | `paper-api.alpaca.markets` |
| Endpoint (Live) | `api.alpaca.markets` |
| Markets | US Equities |
| Order Types | Market, Limit, Stop, Trailing |

---

## AI Configuration

### Poe AI (Recommended)

Poe offers access to multiple AI models including Claude, GPT-4, and Llama.

#### Setup Steps

1. **Get Poe API Key**
   - Visit [poe.com/api](https://poe.com/api)
   - Click "Create API Key"
   - Copy your key (starts with `poa_`)

2. **Select AI Model**

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| Claude Sonnet | General analysis | Fast | Medium |
| Claude Opus | Deep analysis | Slow | High |
| GPT-4o | Multimodal | Fast | Medium |
| Llama 3 | Budget option | Fast | Low |

3. **Configure in Kazzy**
   - Go to Settings → AI Configuration
   - Select "Poe AI"
   - Paste your API key
   - Choose your model
   - Click "Save"

### OpenAI

OpenAI's GPT models offer state-of-the-art language understanding.

#### Setup Steps

1. **Get OpenAI API Key**
   - Visit [platform.openai.com](https://platform.openai.com)
   - Create account or login
   - Go to "API Keys"
   - Click "Create new secret key"
   - Copy key (starts with `sk-`)

2. **Set Up Billing**
   - Add payment method
   - Configure spending limits
   - Monitor usage

3. **Configure in Kazzy**
   - Settings → AI Configuration
   - Select "OpenAI"
   - Paste API key
   - Click "Save"

#### Usage Costs

| Model | Input | Output | Best For |
|-------|-------|--------|----------|
| GPT-4o | $5/1M | $15/1M | General |
| GPT-4-turbo | $10/1M | $30/1M | Fast |
| GPT-3.5 | $0.50/1M | $1.50/1M | Budget |

---

## Trading Commands

### Basic Commands

#### Buy/Sell Orders

```
buy 0.01 BTC          → Market buy Bitcoin
buy 1 ETH             → Market buy Ethereum
sell 0.5 SOL          → Market sell Solana
buy limit BTC 45000   → Limit buy at $45,000
sell limit ETH 3000    → Limit sell at $3,000
```

#### Position Management

```
show positions         → View open positions
close BTC             → Close BTC position
close all             → Close all positions
```

#### Market Information

```
price BTC             → Get BTC current price
quote ETH             → Get ETH quote
balance               → Show account balance
portfolio             → Show full portfolio
```

### AI Commands

#### Trading Automation

```
auto on               → Enable auto-trading
auto off              → Disable auto-trading
automate              → Start AI automation
pause                 → Pause trading
resume                → Resume trading
```

#### Market Analysis

```
analyze BTC           → AI analysis of Bitcoin
analyze ETH           → AI analysis of Ethereum
forecast AAPL         → Stock price forecast
sentiment             → Market sentiment
```

#### Risk Management

```
risk                  → Show risk settings
set risk 2%           → Set risk per trade
max positions 5       → Set max open positions
```

### Advanced Commands

```
limit buy 0.1 BTC @ 40000      → Limit order
stop loss BTC @ 38000           → Set stop loss
take profit ETH @ 3500          → Set take profit
trailing stop 2%               → Enable trailing stop
```

---

## Auto-Trading Setup

### Step-by-Step Configuration

1. **Connect Exchange**
   - Settings → Exchange Connections
   - Select platform
   - Enter API credentials
   - Click "Connect"

2. **Configure Risk Parameters**

| Parameter | Conservative | Moderate | Aggressive |
|-----------|-------------|----------|------------|
| Risk/Trade | 1-2% | 2-5% | 5-10% |
| Max Positions | 3 | 5 | 10 |
| Max Daily Loss | 5% | 10% | 20% |

3. **Select Trading Strategies**

| Strategy | Description | Best Market |
|----------|-------------|-------------|
| RSI | Buy oversold, sell overbought | Ranging |
| MA Crossover | Trend following | Trending |
| Grid | Range-bound orders | Sideways |

4. **Enable Auto-Trading**
   - Toggle "Auto Trading" switch
   - Confirm settings
   - Monitor in dashboard

### Monitoring Auto-Trading

- **Dashboard**: Real-time position monitoring
- **Terminal**: Execution logs
- **Kazzy AI**: Natural language status updates

---

## Risk Management

### Position Sizing Formula

```
Position Size = Account × Risk% / (Entry × Stop Loss%)
```

### Example Calculation

**Account**: $10,000
**Risk**: 2% = $200
**Entry**: $45,000
**Stop Loss**: 5% = $2,250

```
Position = $10,000 × 0.02 / ($45,000 × 0.05)
Position = $200 / $2,250
Position = 0.089 BTC
```

### Risk Rules

| Rule | Conservative | Moderate | Aggressive |
|------|-------------|----------|------------|
| Max Risk/Trade | 2% | 5% | 10% |
| Max Daily Loss | 5% | 10% | 20% |
| Max Positions | 3 | 5 | 10 |
| Max Correlation | 50% | 70% | 90% |

### Emergency Stops

- **Immediate Stop**: Click "Stop All" button
- **Auto Stop**: Triggers when daily loss limit hit
- **Position Limit**: Stops when max positions reached

---

## Troubleshooting

### Common Issues

#### Connection Failed

| Cause | Solution |
|-------|----------|
| Invalid API key | Double-check credentials |
| Wrong permissions | Enable trading permission |
| IP not whitelisted | Add server IP to whitelist |
| Account locked | Contact exchange support |

#### Orders Not Executing

| Cause | Solution |
|-------|----------|
| Insufficient balance | Fund account |
| Market closed | Check market hours |
| Price too far | Adjust order price |
| Risk limit hit | Adjust risk settings |

#### AI Not Responding

| Cause | Solution |
|-------|----------|
| API key invalid | Re-enter API key |
| API quota exceeded | Check usage, upgrade plan |
| Network issue | Check internet connection |

### API Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad Request | Check parameters |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check permissions |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Try again later |

### Support Contact

For additional help:
- Check terminal logs for error details
- Review AI thought log for decisions
- Verify exchange connectivity
- Contact support with error screenshots

---

## Appendix: Supported Assets

### Cryptocurrency

| Symbol | Exchange | Type |
|--------|----------|------|
| BTC/USDT | Binance, Bybit, Coinbase | Spot |
| ETH/USDT | Binance, Bybit, Coinbase | Spot |
| SOL/USDT | Binance, Bybit | Spot |
| XRP/USDT | Binance, Coinbase | Spot |

### Forex

| Symbol | Exchange | Type |
|--------|----------|------|
| EUR/USD | MT4, MT5, cTrader | Spot |
| GBP/USD | MT4, MT5, cTrader | Spot |
| USD/JPY | MT4, MT5, cTrader | Spot |
| XAU/USD | MT4, MT5 | Spot |

### Stocks

| Symbol | Exchange | Type |
|--------|----------|------|
| AAPL | Alpaca, IBKR | Equity |
| MSFT | Alpaca, IBKR | Equity |
| GOOGL | IBKR | Equity |
| TSLA | Alpaca, IBKR | Equity |

### Commodities

| Symbol | Exchange | Type |
|--------|----------|------|
| XAU/USD | MT5, CFDs | Gold |
| XAG/USD | MT5, CFDs | Silver |
| WTI | MT5, CFDs | Oil |
| BRENT | MT5, CFDs | Oil |

---

**Kazzy Agent - Your AI-Powered Trading Partner**

*For the latest updates and documentation, visit our support portal.*
