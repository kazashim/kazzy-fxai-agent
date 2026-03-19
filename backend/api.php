<?php
/**
 * Kazzy Agent - PHP API Wrapper for cPanel
 *
 * This provides basic API endpoints compatible with the frontend
 * For full functionality, use the Python backend on a VPS
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Configuration
$config = [
    'api_url' => 'https://api.binance.com', // Default exchange
    'demo_mode' => true // Set to false when real API keys configured
];

// Get request data
$method = $_SERVER['REQUEST_METHOD'];
$request = $_GET['action'] ?? $_POST['action'] ?? '';
$input = json_decode(file_get_contents('php://input'), true);

// Simple in-memory storage for demo
$storage = [
    'balances' => [],
    'positions' => [],
    'connected_exchanges' => []
];

// Response helper
function respond($success, $data = [], $message = '') {
    echo json_encode([
        'success' => $success,
        'message' => $message,
        'data' => $data,
        'timestamp' => date('c')
    ]);
    exit();
}

// Router
switch ($request) {
    // Health check
    case 'health':
        respond(true, [
            'status' => 'online',
            'mode' => $config['demo_mode'] ? 'demo' : 'live',
            'version' => '1.0.0'
        ]);
        break;

    // Get system status
    case 'status':
        respond(true, [
            'exchanges' => $storage['connected_exchanges'],
            'total_balance' => array_sum(array_column($storage['balances'], 'total')),
            'positions_count' => count($storage['positions']),
            'ai_enabled' => false
        ]);
        break;

    // Connect exchange
    case 'connect':
        $exchange = $input['exchange'] ?? '';
        $apiKey = $input['api_key'] ?? '';
        $apiSecret = $input['api_secret'] ?? '';

        if (empty($exchange) || empty($apiKey)) {
            respond(false, [], 'Exchange and API key required');
        }

        // In demo mode, just save the connection
        if ($config['demo_mode']) {
            $storage['connected_exchanges'][$exchange] = [
                'status' => 'connected',
                'connected_at' => date('c')
            ];
            $storage['balances'][$exchange] = [
                'total' => 10000.00,
                'available' => 10000.00,
                'currency' => 'USD'
            ];
            respond(true, ['exchange' => $exchange], 'Connected (Demo Mode)');
        }

        // Real connection would go here for each exchange
        respond(true, ['exchange' => $exchange], 'Exchange connected');
        break;

    // Get balance
    case 'balance':
        $exchange = $input['exchange'] ?? 'binance';
        if (isset($storage['balances'][$exchange])) {
            respond(true, $storage['balances'][$exchange]);
        }
        respond(true, ['total' => 0, 'available' => 0, 'currency' => 'USD']);
        break;

    // Get positions
    case 'positions':
        respond(true, ['positions' => $storage['positions'], 'count' => count($storage['positions'])]);
        break;

    // Execute trade
    case 'trade':
        $exchange = $input['exchange'] ?? 'binance';
        $symbol = $input['symbol'] ?? 'BTC/USDT';
        $side = $input['side'] ?? 'buy';
        $quantity = floatval($input['quantity'] ?? 0.01);

        // Demo mode - simulate trade
        $trade = [
            'id' => uniqid('trade_'),
            'exchange' => $exchange,
            'symbol' => $symbol,
            'side' => $side,
            'quantity' => $quantity,
            'price' => getDemoPrice($symbol),
            'status' => 'filled',
            'timestamp' => date('c')
        ];

        $storage['positions'][] = $trade;
        respond(true, $trade, 'Trade executed');
        break;

    // Get ticker prices
    case 'tickers':
        $tickers = getDemoTickers();
        respond(true, ['tickers' => $tickers, 'count' => count($tickers)]);
        break;

    // Get price for symbol
    case 'price':
        $symbol = $input['symbol'] ?? 'BTC/USDT';
        respond(true, [
            'symbol' => $symbol,
            'price' => getDemoPrice($symbol),
            'timestamp' => date('c')
        ]);
        break;

    // Close position
    case 'close_position':
        $positionId = $input['position_id'] ?? '';
        // Remove position from array
        foreach ($storage['positions'] as $key => $pos) {
            if ($pos['id'] === $positionId) {
                unset($storage['positions'][$key]);
                respond(true, ['position_id' => $positionId], 'Position closed');
            }
        }
        respond(false, [], 'Position not found');
        break;

    // AI analysis
    case 'analyze':
        $symbol = $input['symbol'] ?? 'BTC/USDT';
        $analysis = [
            'symbol' => $symbol,
            'trend' => ['bullish', 'bearish', 'sideways'][array_rand(['bullish', 'bearish', 'sideways'])],
            'signal' => ['buy', 'sell', 'hold'][array_rand(['buy', 'sell', 'hold'])],
            'confidence' => rand(60, 95),
            'rsi' => rand(30, 70),
            'recommendation' => 'Demo analysis - Configure Poe API for real analysis'
        ];
        respond(true, $analysis);
        break;

    // AI Chat
    case 'chat':
        $message = $input['message'] ?? '';

        $responses = [
            "I'm Kazzy, your AI trading assistant. In demo mode, I can provide general trading guidance.",
            "To enable live trading, please connect your exchange APIs in the Settings tab.",
            "I can help you analyze markets, set up strategies, and manage risk.",
            "For real AI analysis, please configure your Poe API key in Settings."
        ];

        respond(true, [
            'response' => $responses[array_rand($responses)],
            'model' => 'demo'
        ]);
        break;

    // Emergency stop
    case 'emergency_stop':
        $storage['positions'] = [];
        respond(true, [], 'All positions closed - Emergency stop activated');
        break;

    // Default - unknown action
    default:
        respond(false, [], 'Unknown action: ' . $request);
}

/**
 * Get demo prices for various symbols
 */
function getDemoPrice($symbol) {
    $prices = [
        'BTC/USDT' => 67500.00,
        'ETH/USDT' => 3450.00,
        'EUR/USD' => 1.0847,
        'GBP/USD' => 1.2612,
        'XAU/USD' => 2035.50,
        'AAPL' => 178.50,
        'TSLA' => 245.80,
        'NVDA' => 875.50
    ];

    // Add small random variation
    $base = $prices[$symbol] ?? 100.00;
    $variation = $base * (rand(-50, 50) / 10000);
    return round($base + $variation, $symbol === 'EUR/USD' || $symbol === 'GBP/USD' ? 4 : 2);
}

/**
 * Get demo tickers for all symbols
 */
function getDemoTickers() {
    $symbols = [
        'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
        'EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CHF',
        'XAU/USD', 'XAG/USD',
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA',
        'SPY', 'QQQ', 'DIA'
    ];

    $tickers = [];
    foreach ($symbols as $symbol) {
        $price = getDemoPrice($symbol);
        $change = $price * (rand(-100, 100) / 10000);

        $tickers[] = [
            'symbol' => $symbol,
            'price' => $price,
            'change' => $change,
            'changePercent' => ($change / $price) * 100,
            'bid' => $price - ($price * 0.001),
            'ask' => $price + ($price * 0.001),
            'volume' => rand(1000000, 100000000)
        ];
    }

    return $tickers;
}
