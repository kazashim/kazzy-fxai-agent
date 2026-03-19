/**
 * Kazzy Agent - API Service
 * Handles communication between frontend and backend (Python or PHP)
 */

const API_CONFIG = {
    // Primary: Python backend (use your Render/VPS URL)
    // Change this to your deployed backend URL
    pythonApiUrl: 'https://kazzy-agent.onrender.com',

    // Fallback: PHP backend (cPanel compatible)
    phpApiUrl: '/backend/api.php',

    // Which to use: 'python' or 'php'
    mode: 'python', // Change to 'python' when backend is available

    // Timeout settings
    timeout: 30000,

    // Demo mode when no backend
    demoMode: false
};

// Get the appropriate API base URL
export const getApiUrl = () => {
    return API_CONFIG.mode === 'python'
        ? API_CONFIG.pythonApiUrl
        : API_CONFIG.phpApiUrl;
};

// Set API mode
export const setApiMode = (mode) => {
    if (mode === 'python' || mode === 'php') {
        API_CONFIG.mode = mode;
        localStorage.setItem('kazzy_api_mode', mode);
    }
};

// Initialize API mode from storage
export const initApiMode = () => {
    const saved = localStorage.getItem('kazzy_api_mode');
    if (saved === 'python' || saved === 'php') {
        API_CONFIG.mode = saved;
    }
};

// Generic API call handler
export const apiCall = async (action, data = {}, method = 'POST') => {
    const baseUrl = getApiUrl();
    const url = `${baseUrl}?action=${action}`;

    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (method === 'POST' && Object.keys(data).length > 0) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API Error [${action}]:`, error);

        // Return demo response if in demo mode
        if (API_CONFIG.demoMode) {
            return getDemoResponse(action);
        }

        throw error;
    }
};

// Demo responses when backend unavailable
const getDemoResponse = (action) => {
    const demoResponses = {
        health: {
            success: true,
            data: { status: 'demo', mode: 'demo' }
        },
        status: {
            success: true,
            data: {
                exchanges: [],
                total_balance: 0,
                positions_count: 0,
                ai_enabled: false
            }
        },
        balance: {
            success: true,
            data: { total: 10000, available: 10000, currency: 'USD' }
        },
        positions: {
            success: true,
            data: { positions: [], count: 0 }
        },
        tickers: {
            success: true,
            data: { tickers: getDemoTickers(), count: 22 }
        },
        analyze: {
            success: true,
            data: {
                symbol: 'BTC/USDT',
                trend: 'bullish',
                signal: 'buy',
                confidence: 72,
                rsi: 58
            }
        },
        chat: {
            success: true,
            data: {
                response: "I'm Kazzy, your AI trading assistant. Configure your backend for full functionality.",
                model: 'demo'
            }
        }
    };

    return demoResponses[action] || { success: false, message: 'Unknown action' };
};

// Demo ticker data
const getDemoTickers = () => {
    const symbols = [
        { symbol: 'BTC/USDT', price: 67500 },
        { symbol: 'ETH/USDT', price: 3450 },
        { symbol: 'BNB/USDT', price: 580 },
        { symbol: 'SOL/USDT', price: 145 },
        { symbol: 'XRP/USDT', price: 0.52 },
        { symbol: 'EUR/USD', price: 1.0847 },
        { symbol: 'GBP/USD', price: 1.2612 },
        { symbol: 'USD/JPY', price: 149.85 },
        { symbol: 'XAU/USD', price: 2035.50 },
        { symbol: 'AAPL', price: 178.50 },
        { symbol: 'MSFT', price: 405.20 },
        { symbol: 'GOOGL', price: 142.50 },
        { symbol: 'AMZN', price: 178.20 },
        { symbol: 'TSLA', price: 245.80 },
        { symbol: 'NVDA', price: 875.50 }
    ];

    return symbols.map(s => ({
        ...s,
        change: s.price * (Math.random() - 0.5) * 0.02,
        changePercent: (Math.random() - 0.5) * 2
    }));
};

// API Action functions
export const api = {
    // Health check
    health: () => apiCall('health'),

    // System status
    status: () => apiCall('status'),

    // Connect exchange
    connect: (exchange, apiKey, apiSecret, testnet = false) =>
        apiCall('connect', { exchange, api_key: apiKey, api_secret: apiSecret, testnet }),

    // Get balance
    balance: (exchange) => apiCall('balance', { exchange }),

    // Get positions
    positions: (exchange) => apiCall('positions', { exchange }),

    // Execute trade
    trade: (exchange, symbol, side, quantity, orderType = 'market') =>
        apiCall('trade', { exchange, symbol, side, quantity, order_type: orderType }),

    // Get tickers
    tickers: () => apiCall('tickers'),

    // Get price
    price: (symbol) => apiCall('price', { symbol }),

    // Close position
    closePosition: (positionId) => apiCall('close_position', { position_id: positionId }),

    // AI Analyze
    analyze: (symbol) => apiCall('analyze', { symbol }),

    // AI Chat
    chat: (message, context = {}) => apiCall('chat', { message, context }),

    // Emergency stop
    emergencyStop: () => apiCall('emergency_stop'),

    // AI enable/disable
    enableAI: () => apiCall('ai_enable'),
    disableAI: () => apiCall('ai_disable'),

    // Auto trading
    startAutoTrading: (symbols, riskLevel = 'medium', maxPositions = 5) =>
        apiCall('auto_start', { symbols, risk_level: riskLevel, max_positions: maxPositions }),
    stopAutoTrading: () => apiCall('auto_stop'),

    // Live feeds
    startFeeds: () => apiCall('feeds_start'),
    stopFeeds: () => apiCall('feeds_stop'),
    getFeedsStatus: () => apiCall('feeds_status'),
    getPrices: () => apiCall('prices')
};

export default api;
