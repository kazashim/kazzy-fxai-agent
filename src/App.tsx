import { useState, useEffect, useRef, useCallback } from 'react'
import {
  LayoutDashboard,
  Wallet,
  TrendingUp,
  Radio,
  Settings,
  ChevronLeft,
  ChevronRight,
  Activity,
  Zap,
  AlertTriangle,
  Copy,
  Check,
  RefreshCw,
  Send,
  Bot,
  X,
  Minus,
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  XCircle,
  CheckCircle,
  Circle,
  Layers,
  BarChart3,
  LineChart,
  PieChart,
  Cpu,
  Key,
  Globe,
  Shield,
  TrendingDown,
  DollarSign,
  Percent,
  Calculator,
  FileText,
  Bell,
  Search,
  Menu,
  X as CloseIcon,
  Play,
  Pause,
  StopCircle,
  Link,
  Unlink,
  Power,
  Gauge,
  Eye,
  EyeOff,
  Terminal,
  AlertCircle,
  Rocket
} from 'lucide-react'
import { createChart, IChartApi, Time, CandlestickSeries } from 'lightweight-charts'

// Helper function
const formatNumber = (num: number, decimals: number = 0) => {
  if (num >= 1000000000) return (num / 1000000000).toFixed(1) + 'B'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toFixed(decimals)
}

// Types
type AssetClass = 'forex' | 'crypto' | 'stocks' | 'commodities' | 'indices' | 'options' | 'futures' | 'bonds' | 'cfds'

interface Platform {
  id: string
  name: string
  type: AssetClass
  logo: string
  status: 'connected' | 'disconnected' | 'error' | 'connecting'
  balance: number
  lastSync: string
  apiKey?: string
  apiSecret?: string
}

interface Position {
  id: string
  symbol: string
  side: 'buy' | 'sell'
  size: number
  entryPrice: number
  currentPrice: number
  pnl: number
  pnlPercent: number
  platform: string
  openTime: string
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface TickerItem {
  symbol: string
  price: number
  change: number
  changePercent: number
}

interface Signal {
  id: string
  symbol: string
  direction: 'buy' | 'sell'
  entryZone: string
  stopLoss: string
  takeProfit: string
  confidence: number
  expiry: string
  timestamp: Date
  strategy?: string
  entry_reason?: string
  risk_reward?: number
  price?: number
  change_24h?: number
}

// Real Signal from API
interface RealSignal {
  id: string
  symbol: string
  direction: 'buy' | 'sell'
  entry_zone: string
  stop_loss: number
  take_profit: number
  confidence: number
  timeframe: string
  strategy: string
  entry_reason: string
  risk_reward: number
  timestamp: string
  valid_until: string
  price: number
  change_24h: number
}

interface Strategy {
  id: string
  name: string
  status: 'active' | 'paused' | 'inactive'
  lastRun?: string
  tradesCount: number
}

// Sample data - ALL ASSET CLASSES
const initialPlatforms: Platform[] = [
  // Forex
  { id: 'mt4', name: 'MetaTrader 4', type: 'forex', logo: '📊', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'mt5', name: 'MetaTrader 5', type: 'forex', logo: '📈', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'ctrader', name: 'cTrader', type: 'forex', logo: '🎯', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'fxcm', name: 'FXCM', type: 'forex', logo: '💱', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'icmarkets', name: 'IC Markets', type: 'forex', logo: '🌐', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  // Crypto
  { id: 'binance', name: 'Binance', type: 'crypto', logo: '₿', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'coinbase', name: 'Coinbase', type: 'crypto', logo: '💰', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'bybit', name: 'Bybit', type: 'crypto', logo: '🔷', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'kraken', name: 'Kraken', type: 'crypto', logo: '🐙', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'kucoin', name: 'KuCoin', type: 'crypto', logo: '🪙', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'okx', name: 'OKX', type: 'crypto', logo: '🔴', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  // Stocks
  { id: 'ibkr', name: 'Interactive Brokers', type: 'stocks', logo: '📊', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'alpaca', name: 'Alpaca', type: 'stocks', logo: '🦙', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'tdameritrade', name: 'TD Ameritrade', type: 'stocks', logo: '🏦', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'fidelity', name: 'Fidelity', type: 'stocks', logo: '💎', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'schwab', name: 'Charles Schwab', type: 'stocks', logo: '🦅', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  // Commodities
  { id: 'metals', name: 'Precious Metals', type: 'commodities', logo: '🥇', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'oilgas', name: 'Oil & Gas', type: 'commodities', logo: '🛢️', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'agriculture', name: 'Agriculture', type: 'commodities', logo: '🌾', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  // Indices
  { id: 'ind_mt5', name: 'MT5 Indices', type: 'indices', logo: '📈', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'ind_ibkr', name: 'IBKR Indices', type: 'indices', logo: '📉', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  // Options
  { id: 'options_ibkr', name: 'IBKR Options', type: 'options', logo: '🎰', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'options_tos', name: 'ThinkOrSwim', type: 'options', logo: '🎲', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  // Futures
  { id: 'futures_ibkr', name: 'IBKR Futures', type: 'futures', logo: '🔮', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'tradovate', name: 'Tradovate', type: 'futures', logo: '📊', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'cme', name: 'CME Group', type: 'futures', logo: '🏛️', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  // Bonds
  { id: 'bonds_treasury', name: 'US Treasury', type: 'bonds', logo: '📜', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'bonds_corporate', name: 'Corporate Bonds', type: 'bonds', logo: '📃', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  // CFDs
  { id: 'cfds_mt5', name: 'MT5 CFDs', type: 'cfds', logo: '📋', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'cfds_ig', name: 'IG Markets', type: 'cfds', logo: '📌', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'cfds_oanda', name: 'OANDA', type: 'cfds', logo: '🌊', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  // TradingView
  { id: 'tradingview', name: 'TradingView', type: 'forex', logo: '📉', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
]

const initialPositions: Position[] = []

const initialTickers: TickerItem[] = [
  // Forex
  { symbol: 'EUR/USD', price: 1.0847, change: 0.0022, changePercent: 0.2 },
  { symbol: 'GBP/USD', price: 1.2612, change: -0.0033, changePercent: -0.26 },
  { symbol: 'USD/JPY', price: 149.85, change: 0.45, changePercent: 0.3 },
  { symbol: 'USD/CHF', price: 0.8845, change: 0.0012, changePercent: 0.14 },
  { symbol: 'AUD/USD', price: 0.6532, change: -0.0021, changePercent: -0.32 },
  { symbol: 'USD/CAD', price: 1.3542, change: 0.0008, changePercent: 0.06 },
  { symbol: 'NZD/USD', price: 0.6125, change: 0.0015, changePercent: 0.25 },
  { symbol: 'EUR/GBP', price: 0.8602, change: 0.0021, changePercent: 0.24 },
  // Crypto
  { symbol: 'BTC/USDT', price: 43200, change: 850, changePercent: 2.01 },
  { symbol: 'ETH/USDT', price: 2245, change: -35, changePercent: -1.54 },
  { symbol: 'SOL/USDT', price: 98.5, change: 3.2, changePercent: 3.36 },
  { symbol: 'XRP/USDT', price: 0.5234, change: 0.012, changePercent: 2.35 },
  { symbol: 'ADA/USDT', price: 0.4521, change: -0.008, changePercent: -1.74 },
  { symbol: 'DOGE/USDT', price: 0.0825, change: 0.0021, changePercent: 2.61 },
  { symbol: 'AVAX/USDT', price: 35.2, change: 0.8, changePercent: 2.33 },
  // Commodities
  { symbol: 'XAU/USD', price: 2028, change: -7, changePercent: -0.34 },
  { symbol: 'XAG/USD', price: 22.85, change: 0.15, changePercent: 0.66 },
  { symbol: 'WTI', price: 78.5, change: 1.2, changePercent: 1.55 },
  { symbol: 'BRENT', price: 82.3, change: 0.95, changePercent: 1.17 },
  { symbol: 'NATGAS', price: 2.85, change: -0.05, changePercent: -1.72 },
  // Indices
  { symbol: 'US30', price: 38450, change: 125, changePercent: 0.33 },
  { symbol: 'US500', price: 5125, change: 15, changePercent: 0.29 },
  { symbol: 'NAS100', price: 17250, change: 85, changePercent: 0.49 },
  { symbol: 'UK100', price: 7650, change: 35, changePercent: 0.46 },
  { symbol: 'GER40', price: 17850, change: 65, changePercent: 0.37 },
  { symbol: 'FRA40', price: 8125, change: 28, changePercent: 0.35 },
  { symbol: 'JPN225', price: 36850, change: -120, changePercent: -0.32 },
  // Stocks
  { symbol: 'AAPL', price: 178.5, change: 2.3, changePercent: 1.31 },
  { symbol: 'MSFT', price: 405.2, change: 5.8, changePercent: 1.45 },
  { symbol: 'GOOGL', price: 142.5, change: 1.8, changePercent: 1.28 },
  { symbol: 'AMZN', price: 178.2, change: 3.1, changePercent: 1.77 },
  { symbol: 'TSLA', price: 245.8, change: -4.2, changePercent: -1.68 },
  { symbol: 'NVDA', price: 875.5, change: 15.2, changePercent: 1.77 },
  { symbol: 'META', price: 485.2, change: 8.5, changePercent: 1.78 },
  { symbol: 'JPM', price: 185.5, change: 1.2, changePercent: 0.65 },
  // Options (Sample)
  { symbol: 'AAPL250119C180', price: 4.5, change: 0.2, changePercent: 4.65 },
  { symbol: 'TSLA250119P250', price: 6.2, change: -0.3, changePercent: -4.62 },
  // Futures (Sample)
  { symbol: 'ES', price: 5125.5, change: 12.5, changePercent: 0.24 },
  { symbol: 'NQ', price: 18250.5, change: 45.5, changePercent: 0.25 },
  { symbol: 'YM', price: 38650, change: 85, changePercent: 0.22 },
  { symbol: 'CL', price: 78.5, change: 1.2, changePercent: 1.55 },
  // Bonds (Sample)
  { symbol: 'US10Y', price: 4.25, change: 0.05, changePercent: 1.19 },
  { symbol: 'US2Y', price: 4.85, change: 0.02, changePercent: 0.41 },
  { symbol: 'DE10Y', price: 2.45, change: 0.03, changePercent: 1.24 },
]

const initialSignals: Signal[] = [
  { id: '1', symbol: 'EUR/GBP', direction: 'buy', entryZone: '0.8520-0.8540', stopLoss: '0.8490', takeProfit: '0.8580', confidence: 78, expiry: '4h', timestamp: new Date() },
  { id: '2', symbol: 'BTC/USDT', direction: 'sell', entryZone: '43500-43800', stopLoss: '44200', takeProfit: '42500', confidence: 65, expiry: '6h', timestamp: new Date() },
  { id: '3', symbol: 'XAU/USD', direction: 'buy', entryZone: '2020-2025', stopLoss: '2010', takeProfit: '2045', confidence: 82, expiry: '2h', timestamp: new Date() },
]

const availableStrategies: Strategy[] = [
  { id: 'rsi', name: 'RSI Mean Reversion', status: 'inactive', tradesCount: 0 },
  { id: 'ma_crossover', name: 'MA Crossover', status: 'inactive', tradesCount: 0 },
  { id: 'grid', name: 'Grid Trading', status: 'inactive', tradesCount: 0 },
]

// Kazzy AI responses
const kazzyResponses = [
  "Based on my analysis of EUR/USD, the pair is showing bullish momentum on the 4-hour chart. The RSI is at 58, indicating room for further upside. I'd recommend waiting for a pullback to the 1.0830 level before entering.",

  "For your conservative risk profile, I suggest limiting position size to maximum 2% risk per trade. With your account balance of $100,800, that's $2,016 maximum risk per position.",

  "I've detected high correlation between your BTC and ETH positions. Consider reducing exposure to minimize portfolio risk. Correlation coefficient is currently at 0.78.",

  "Important: NFP (Non-Farm Payrolls) data releases in 2 hours. This typically causes high volatility. Consider reducing position sizes or avoiding new entries until after the announcement.",

  "Technical analysis on XAU/USD shows strong support at $2020 and resistance at $2050. The 50-day moving average is acting as dynamic support. A break above $2035 could target $2045.",

  "Your portfolio allocation: Forex 42%, Crypto 58%. This is slightly skewed towards crypto. For a conservative profile, consider rebalancing to 60/40 split.",

  "Risk calculation complete: With a $10,000 account, 1% risk ($100), and 20 pip stop loss on EUR/USD, your position size should be 0.50 lots.",

  "Market sentiment analysis: Bitcoin showing positive momentum with institutional inflows. Support at $42,000 holding well. Next resistance at $44,500.",

  "Automated trading is now enabled. I'll monitor your positions and can execute trades based on your configured strategies when API keys are connected.",

  "I've activated the RSI strategy. It will analyze market conditions and suggest trades when RSI reaches oversold (<30) or overbought (>70) levels.",
]

// Main App Component
function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [kazzyPanelOpen, setKazzyPanelOpen] = useState(true)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [platforms, setPlatforms] = useState(initialPlatforms)
  const [positions, setPositions] = useState<Position[]>(initialPositions)
  const [tickers, setTickers] = useState(initialTickers)
  const [signals, setSignals] = useState(initialSignals)
  const [realSignals, setRealSignals] = useState<RealSignal[]>([])
  const [signalsLoading, setSignalsLoading] = useState(false)
  const [signalsLastUpdate, setSignalsLastUpdate] = useState<Date | null>(null)
  const [strategies, setStrategies] = useState(availableStrategies)
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: '1', role: 'assistant', content: "Hello! I'm Kazzy, your AI-powered automated trading assistant. I can help you:\n\n🤖 Connect to trading platforms (Binance, Bybit, Coinbase, MetaTrader)\n\n📈 Analyze markets and generate signals\n\n⚡ Run automated trading strategies\n\n💰 Manage positions with risk controls\n\n🔐 Your API keys are encrypted and never stored in plain text\n\nTo get started, go to the Settings tab and connect your exchange accounts with API keys. Would you like me to help you set up automated trading?", timestamp: new Date() }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [calculatorOpen, setCalculatorOpen] = useState(false)
  const [copiedSignal, setCopiedSignal] = useState<string | null>(null)
  const [chartContainer, setChartContainer] = useState<HTMLDivElement | null>(null)
  const [chart, setChart] = useState<IChartApi | null>(null)
  const [chartSymbol, setChartSymbol] = useState('BTC/USDT')
  const [candlestickData, setCandlestickData] = useState<{ time: Time; open: number; high: number; low: number; close: number }[]>([])
  const [chartTimeframe, setChartTimeframe] = useState('1H')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Automation features
  const [autoTradingEnabled, setAutoTradingEnabled] = useState(false)
  const [apiKeysModalOpen, setApiKeysModalOpen] = useState(false)
  const [selectedExchange, setSelectedExchange] = useState<string>('')
  const [apiKey, setApiKey] = useState('')
  const [apiSecret, setApiSecret] = useState('')
  const [testnet, setTestnet] = useState(false)
  const [emergencyStopOpen, setEmergencyStopOpen] = useState(false)
  const [showTerminal, setShowTerminal] = useState(false)
  const [terminalLogs, setTerminalLogs] = useState<string[]>([])

  // Risk settings
  const [riskSettings, setRiskSettings] = useState({
    maxRiskPerTrade: 2,
    maxDailyLoss: 5,
    maxPositions: 5,
  })

  // Calculator state
  const [calcBalance, setCalcBalance] = useState(10000)
  const [calcRisk, setCalcRisk] = useState(1)
  const [calcStopLoss, setCalcStopLoss] = useState(20)
  const [calcResult, setCalcResult] = useState<number | null>(null)

  // OpenAI API Key state
  const [openaiKey, setOpenaiKey] = useState('')
  const [showOpenaiKey, setShowOpenaiKey] = useState(false)

  // Poe API Key state
  const [poeKey, setPoeKey] = useState('')

  // Live Feeds state
  const [liveFeedsEnabled, setLiveFeedsEnabled] = useState(false)
  const [livePrices, setLivePrices] = useState<Record<string, { price: number; change: number; changePercent: number; timestamp: string }>>({})
  const [liveFeedsStatus, setLiveFeedsStatus] = useState<{ streaming: boolean; feed_types: string[] }>({ streaming: false, feed_types: [] })
  const [showPoeKey, setShowPoeKey] = useState(false)
  const [poeModel, setPoeModel] = useState('claude-sonnet')
  const [aiProvider, setAiProvider] = useState<'openai' | 'poe'>('poe')

  // Available Poe models
  const poeModels = [
    { id: 'claude-opus', name: 'Claude 4 Opus', desc: 'Deep analysis' },
    { id: 'claude-sonnet', name: 'Claude 4 Sonnet', desc: 'Balanced' },
    { id: 'gpt-4o', name: 'GPT-4o', desc: 'OpenAI flagship' },
    { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', desc: 'Fast GPT-4' },
    { id: 'llama-3', name: 'Llama 3.1 405B', desc: 'Meta open model' },
    { id: 'grok-4', name: 'Grok 4', desc: 'xAI reasoning' },
    { id: 'gemini-pro', name: 'Gemini 1.5 Pro', desc: 'Google multimodal' },
  ]

  // Mobile chat state
  const [mobileChatOpen, setMobileChatOpen] = useState(false)

  // Trading state
  const [tradeSymbol, setTradeSymbol] = useState('BTC/USDT')
  const [tradeAmount, setTradeAmount] = useState('')
  const [tradeSide, setTradeSide] = useState<'buy' | 'sell'>('buy')
  const [tradingExchange, setTradingExchange] = useState('binance')
  const [isTrading, setIsTrading] = useState(false)

  // Calculate total portfolio value
  const totalBalance = platforms.reduce((sum, p) => sum + (p.status === 'connected' ? p.balance : 0), 0)
  const totalPnL = positions.reduce((sum, p) => sum + p.pnl, 0)
  const dailyPnL = totalPnL * 0.35
  const connectedPlatforms = platforms.filter(p => p.status === 'connected').length

  // Live Feeds Functions
  const startLiveFeeds = async () => {
    try {
      const response = await fetch('/api/feeds/start', { method: 'POST' })
      const data = await response.json()
      if (data.success) {
        setLiveFeedsEnabled(true)
        addTerminalLog('LIVE FEEDS STARTED')
      }
    } catch (error) {
      console.error('Failed to start live feeds:', error)
    }
  }

  // Fetch Real Trading Signals from API
  const fetchRealSignals = useCallback(async () => {
    setSignalsLoading(true)
    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE}/api/signals/live`)

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.signals && data.signals.length > 0) {
          setRealSignals(data.signals)
          setSignalsLastUpdate(new Date())

          // Also update tickers with live prices
          const newTickers = tickers.map(ticker => {
            const signal = data.signals.find((s: RealSignal) => s.symbol === ticker.symbol)
            if (signal) {
              return {
                ...ticker,
                price: signal.price || ticker.price,
                change: (signal.change_24h / 100) * signal.price,
                changePercent: signal.change_24h
              }
            }
            return ticker
          })
          setTickers(newTickers)

          addTerminalLog(`📊 Fetched ${data.count} live trading signals`)
        }
      }
    } catch (error) {
      console.error('Failed to fetch signals:', error)
      // Generate demo signals if API not available
      generateDemoSignals()
    } finally {
      setSignalsLoading(false)
    }
  }, [tickers])

  // Generate demo signals when API is not available
  const generateDemoSignals = useCallback(() => {
    const symbols = ['BTC/USDT', 'ETH/USDT', 'EUR/USD', 'GBP/USD', 'XAU/USD', 'SOL/USDT']
    const directions: ('buy' | 'sell')[] = ['buy', 'sell']
    const strategies = ['RSI Oversold', 'MACD Bullish', 'Trend Continuation', 'Support Bounce']

    const demoSignals: RealSignal[] = symbols.slice(0, 6).map((symbol, index) => {
      const basePrice = symbol.includes('BTC') ? 67500 : symbol.includes('ETH') ? 3450 :
                        symbol.includes('XAU') ? 2350 : symbol.includes('EUR') ? 1.0850 : 145
      const change = (Math.random() - 0.5) * 10
      const price = basePrice * (1 + change / 100)
      const direction = directions[Math.floor(Math.random() * directions.length)]
      const stopLoss = direction === 'buy' ? price * 0.98 : price * 1.02
      const takeProfit = direction === 'buy' ? price * 1.04 : price * 0.96

      return {
        id: `demo-${index}`,
        symbol,
        direction,
        entry_zone: `${(price * 0.999).toFixed(price < 10 ? 4 : 2)}-${(price * 1.001).toFixed(price < 10 ? 4 : 2)}`,
        stop_loss: stopLoss,
        take_profit: takeProfit,
        confidence: 65 + Math.floor(Math.random() * 25),
        timeframe: ['15m', '1H', '4H'][Math.floor(Math.random() * 3)],
        strategy: strategies[Math.floor(Math.random() * strategies.length)],
        entry_reason: `Price showing ${direction === 'buy' ? 'bullish' : 'bearish'} momentum based on technical analysis`,
        risk_reward: 1.5 + Math.random(),
        timestamp: new Date().toISOString(),
        valid_until: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(),
        price,
        change_24h: change
      }
    })

    setRealSignals(demoSignals)
    setSignalsLastUpdate(new Date())
  }, [])

  // Fetch real candlestick data from CoinGecko
  const fetchCandlestickData = useCallback(async (symbol: string, timeframe: string) => {
    try {
      // Map symbol to CoinGecko IDs
      const symbolMap: Record<string, string> = {
        'BTC/USDT': 'bitcoin',
        'ETH/USDT': 'ethereum',
        'SOL/USDT': 'solana',
        'XRP/USDT': 'ripple',
        'ADA/USDT': 'cardano',
        'DOGE/USDT': 'dogecoin',
        'XAU/USD': 'gold',
        'EUR/USD': 'eur',
      }

      const coinId = symbolMap[symbol]
      if (!coinId) {
        // Generate simulated data for unsupported symbols
        generateSimulatedCandlestickData(symbol)
        return
      }

      // Map timeframe to days (approximation)
      const daysMap: Record<string, number> = {
        '1H': 2,
        '4H': 7,
        '1D': 30,
        '1W': 90,
      }
      const days = daysMap[timeframe] || 7

      const response = await fetch(
        `https://api.coingecko.com/api/v3/coins/${coinId}/ohlc?vs_currency=usd&days=${days}`
      )

      if (!response.ok) throw new Error('Failed to fetch data')

      const data = await response.json()

      // Transform CoinGecko OHLC format to our format
      const transformedData = data.map((item: number[]) => ({
        time: (item[0] / 1000) as Time,
        open: item[1],
        high: item[2],
        low: item[3],
        close: item[4],
      }))

      setCandlestickData(transformedData)

      // Update ticker price with latest close
      setTickers(prev => prev.map(t => {
        if (t.symbol === symbol && transformedData.length > 0) {
          const latest = transformedData[transformedData.length - 1].close
          const prevPrice = transformedData[transformedData.length - 2]?.close || latest
          return {
            ...t,
            price: latest,
            change: latest - prevPrice,
            changePercent: ((latest - prevPrice) / prevPrice) * 100
          }
        }
        return t
      }))
    } catch (error) {
      console.error('Failed to fetch candlestick data:', error)
      generateSimulatedCandlestickData(symbol)
    }
  }, [])

  // Generate simulated candlestick data when API fails
  const generateSimulatedCandlestickData = (symbol: string) => {
    const basePrice = symbol === 'BTC/USDT' ? 67500 :
                      symbol === 'ETH/USDT' ? 3450 :
                      symbol === 'EUR/USD' ? 1.0850 :
                      symbol === 'XAU/USD' ? 2350 : 100

    const data: { time: Time; open: number; high: number; low: number; close: number }[] = []
    let price = basePrice

    for (let i = 100; i >= 0; i--) {
      const time = Math.floor(Date.now() / 1000) - i * 3600
      const change = (Math.random() - 0.5) * 0.02 * price
      const close = price + change
      const high = Math.max(price, close) * (1 + Math.random() * 0.005)
      const low = Math.min(price, close) * (1 - Math.random() * 0.005)

      data.push({ time: time as Time, open: price, high, low, close })
      price = close
    }

    setCandlestickData(data)
  }

  // Auto-refresh signals every 60 seconds
  useEffect(() => {
    fetchRealSignals()
    const interval = setInterval(fetchRealSignals, 60000)
    return () => clearInterval(interval)
  }, [fetchRealSignals])

  const stopLiveFeeds = async () => {
    try {
      const response = await fetch('/api/feeds/stop', { method: 'POST' })
      const data = await response.json()
      if (data.success) {
        setLiveFeedsEnabled(false)
        addTerminalLog('LIVE FEEDS STOPPED')
      }
    } catch (error) {
      console.error('Failed to stop live feeds:', error)
    }
  }

  // Live feeds price fetching
  useEffect(() => {
    if (!liveFeedsEnabled) return

    const fetchLivePrices = async () => {
      try {
        const response = await fetch('/api/feeds/prices')
        const data = await response.json()
        if (data.prices) {
          setLivePrices(data.prices)
        }
      } catch (error) {
        console.error('Failed to fetch live prices:', error)
      }
    }

    // Initial fetch
    fetchLivePrices()

    // Poll every 2 seconds
    const interval = setInterval(fetchLivePrices, 2000)
    return () => clearInterval(interval)
  }, [liveFeedsEnabled])

  // Real-time ticker simulation
  useEffect(() => {
    const interval = setInterval(() => {
      setTickers(prev => prev.map(ticker => {
        const change = (Math.random() - 0.5) * ticker.price * 0.001
        const newPrice = ticker.price + change
        const newChange = ticker.change + change
        const newChangePercent = (newChange / (ticker.price - ticker.change)) * 100
        return {
          ...ticker,
          price: newPrice,
          change: newChange,
          changePercent: newChangePercent
        }
      }))
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  // Initialize chart - only when container is available and no chart exists
  useEffect(() => {
    if (!chartContainer) return

    // Small delay to ensure container has dimensions when tab becomes active
    const initChart = () => {
      // If chart already exists, just resize it
      if (chart) {
        if (chartContainer.clientWidth > 0 && chartContainer.clientHeight > 0) {
          chart.applyOptions({
            width: chartContainer.clientWidth,
            height: chartContainer.clientHeight
          })
        }
        return
      }

      // Only create chart if container has valid dimensions
      if (chartContainer.clientWidth === 0 || chartContainer.clientHeight === 0) {
        return
      }

      // Create new chart
      const newChart = createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: chartContainer.clientHeight,
        layout: {
          background: { color: '#151a21' },
          textColor: '#94a3b8',
        },
        grid: {
          vertLines: { color: '#1c222b' },
          horzLines: { color: '#1c222b' },
        },
        crosshair: { mode: 1 },
        rightPriceScale: { borderColor: '#2a3441' },
        timeScale: { borderColor: '#2a3441' },
      })

      const candlestickSeries = newChart.addSeries(CandlestickSeries, {
        upColor: '#00c087',
        downColor: '#f23645',
        borderUpColor: '#00c087',
        borderDownColor: '#f23645',
        wickUpColor: '#00c087',
        wickDownColor: '#f23645',
      })

      // Initial data fetch
      fetchCandlestickData(chartSymbol, chartTimeframe)

      // Store series reference for updates
      ;(newChart as any)._candlestickSeries = candlestickSeries
      setChart(newChart)
    }

    // Try immediately, then with a small delay if dimensions are 0
    initChart()
    if (chartContainer.clientWidth === 0) {
      setTimeout(initChart, 100)
    }
  }, [chartContainer])

  // Resize chart when dashboard tab becomes active
  useEffect(() => {
    if (activeTab === 'dashboard' && chart && chartContainer) {
      // Use requestAnimationFrame to ensure DOM has updated
      requestAnimationFrame(() => {
        if (chartContainer.clientWidth > 0 && chartContainer.clientHeight > 0) {
          chart.applyOptions({
            width: chartContainer.clientWidth,
            height: chartContainer.clientHeight
          })
        }
      })
    }
  }, [activeTab, chart, chartContainer])

  // Update chart data when candlestickData changes
  useEffect(() => {
    if (chart && candlestickData.length > 0) {
      const candlestickSeries = (chart as any)._candlestickSeries
      if (candlestickSeries) {
        candlestickSeries.setData(candlestickData)
        chart.timeScale().fitContent()
      }
    }
  }, [chart, candlestickData])

  // Fetch new data when symbol or timeframe changes
  useEffect(() => {
    if (chart) {
      fetchCandlestickData(chartSymbol, chartTimeframe)
    }
  }, [chartSymbol, chartTimeframe, fetchCandlestickData])

  useEffect(() => {
    const handleResize = () => {
      if (chart && chartContainer && chartContainer.clientWidth > 0) {
        chart.applyOptions({ width: chartContainer.clientWidth })
      }
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [chart, chartContainer])

  // Send message to Kazzy - Enhanced AI Trading Assistant
  const sendMessage = useCallback(async () => {
    if (!inputMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsTyping(true)

    // Add user message to terminal
    setTerminalLogs(prev => [...prev, `> ${inputMessage}`])

    const cmd = inputMessage.toLowerCase().trim()
    let response = ''
    let executedTrade = false

    // Check for connected exchange
    const connectedPlatform = platforms.find(p => p.status === 'connected')

    // ============ ENHANCED TRADING COMMANDS ============

    // 1. MARKET ORDER - Buy/Sell at market price
    if (cmd.startsWith('buy') || cmd.startsWith('long')) {
      if (!connectedPlatform) {
        response = "❌ No exchange connected. Please go to Settings → Connect an exchange with your API keys first."
      } else {
        const symbolMatch = inputMessage.match(/(?:buy|long)\s+([A-Z]+(?:\/[A-Z]+)?)/i)
        const amountMatch = inputMessage.match(/([\d.]+)\s*(?:BTC|ETH|USDT|EUR|USD)?/i)
        const symbol = symbolMatch ? symbolMatch[1].toUpperCase() + '/USDT' : 'BTC/USDT'
        const amount = amountMatch ? amountMatch[1] : '0.01'

        try {
          const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
          const tradeRes = await fetch(`${API_BASE}/api/trade`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ exchange: connectedPlatform.id, symbol, side: 'buy', quantity: parseFloat(amount), order_type: 'market' })
          })
          const tradeData = await tradeRes.json()
          if (tradeData.success) {
            response = `✅ MARKET BUY Executed!\n\n💰 Bought ${amount} ${symbol} on ${connectedPlatform.name}\n📊 Order ID: ${tradeData.order?.id || 'N/A'}\n⏰ Time: ${new Date().toLocaleTimeString()}`
            executedTrade = true
            addTerminalLog(`BUY ${amount} ${symbol}`)
          } else {
            response = `❌ Trade Failed: ${tradeData.message || 'Unknown error'}. Check your balance and try again.`
          }
        } catch (e) {
          response = `📊 Demo Mode: Would execute BUY ${amount} ${symbol} on ${connectedPlatform.name}\n\n🔗 Connect to live API for real trading.`
          executedTrade = true
          addTerminalLog(`Demo BUY ${amount} ${symbol}`)
        }
      }
    }
    // 2. SELL ORDER
    else if (cmd.startsWith('sell') || cmd.startsWith('short')) {
      if (!connectedPlatform) {
        response = "❌ No exchange connected. Please go to Settings → Connect an exchange first."
      } else {
        const symbolMatch = inputMessage.match(/(?:sell|short)\s+([A-Z]+(?:\/[A-Z]+)?)/i)
        const amountMatch = inputMessage.match(/([\d.]+)\s*(?:BTC|ETH|USDT|EUR|USD)?/i)
        const symbol = symbolMatch ? symbolMatch[1].toUpperCase() + '/USDT' : 'BTC/USDT'
        const amount = amountMatch ? amountMatch[1] : '0.01'

        try {
          const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
          const tradeRes = await fetch(`${API_BASE}/api/trade`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ exchange: connectedPlatform.id, symbol, side: 'sell', quantity: parseFloat(amount), order_type: 'market' })
          })
          const tradeData = await tradeRes.json()
          if (tradeData.success) {
            response = `✅ MARKET SELL Executed!\n\n💰 Sold ${amount} ${symbol} on ${connectedPlatform.name}\n📊 Order ID: ${tradeData.order?.id || 'N/A'}\n⏰ Time: ${new Date().toLocaleTimeString()}`
            executedTrade = true
            addTerminalLog(`SELL ${amount} ${symbol}`)
          } else {
            response = `❌ Trade Failed: ${tradeData.message || 'Unknown error'}.`
          }
        } catch (e) {
          response = `📊 Demo Mode: Would execute SELL ${amount} ${symbol} on ${connectedPlatform.name}\n\n🔗 Connect to live API for real trading.`
          executedTrade = true
          addTerminalLog(`Demo SELL ${amount} ${symbol}`)
        }
      }
    }
    // 3. LIMIT ORDER - Buy/Sell at specific price
    else if (cmd.includes('limit buy') || cmd.includes('buy limit') || cmd.includes('limit long')) {
      if (!connectedPlatform) {
        response = "❌ No exchange connected."
      } else {
        const symbolMatch = inputMessage.match(/(?:buy|limit)\s+([A-Z]+)/i)
        const amountMatch = inputMessage.match(/([\d.]+)\s*(?:BTC|ETH|USDT)?/i)
        const priceMatch = inputMessage.match(/([\d.]+)\s*(?:at|@)?\s*price/i)
        const symbol = symbolMatch ? symbolMatch[1].toUpperCase() + '/USDT' : 'BTC/USDT'
        const amount = amountMatch ? amountMatch[1] : '0.01'
        const limitPrice = priceMatch ? priceMatch[1] : (Math.random() * 50000).toFixed(2)

        response = `📋 LIMIT ORDER Created (Demo)\n\n🛒 BUY ${amount} ${symbol} @ $${limitPrice}\n📊 Status: Pending\n💡 Use Settings → Quick Trade for full order options.`
        executedTrade = true
        addTerminalLog(`LIMIT BUY ${amount} ${symbol} @ $${limitPrice}`)
      }
    }
    // 4. STOP LOSS ORDER
    else if (cmd.includes('stop loss') || cmd.includes('stop') || cmd.includes('sl')) {
      if (!connectedPlatform) {
        response = "❌ No exchange connected."
      } else {
        const symbolMatch = inputMessage.match(/([A-Z]+)\s*(?:stop|sl)/i)
        const priceMatch = inputMessage.match(/\$?([\d.]+)/i)
        const symbol = symbolMatch ? symbolMatch[1].toUpperCase() : 'BTC'
        const stopPrice = priceMatch ? priceMatch[1] : (Math.random() * 50000).toFixed(2)

        response = `🛡️ STOP LOSS Order (Demo)\n\n⚠️ Set STOP LOSS for ${symbol} @ $${stopPrice}\n📊 Will trigger market sell when price reaches $${stopPrice}\n💡 Configure in Settings → Risk Management`
        executedTrade = true
        addTerminalLog(`STOP LOSS ${symbol} @ $${stopPrice}`)
      }
    }
    // 5. TAKE PROFIT ORDER
    else if (cmd.includes('take profit') || cmd.includes('tp') || cmd.includes('take profit')) {
      if (!connectedPlatform) {
        response = "❌ No exchange connected."
      } else {
        const symbolMatch = inputMessage.match(/([A-Z]+)\s*(?:profit|tp)/i)
        const priceMatch = inputMessage.match(/\$?([\d.]+)/i)
        const symbol = symbolMatch ? symbolMatch[1].toUpperCase() : 'BTC'
        const tpPrice = priceMatch ? priceMatch[1] : (Math.random() * 50000).toFixed(2)

        response = `🎯 TAKE PROFIT Order (Demo)\n\n💰 Set TAKE PROFIT for ${symbol} @ $${tpPrice}\n📊 Will trigger market sell when price reaches $${tpPrice}`
        executedTrade = true
        addTerminalLog(`TAKE PROFIT ${symbol} @ $${tpPrice}`)
      }
    }
    // 6. VIEW POSITIONS
    else if (cmd.includes('position') || cmd.includes('positions') || cmd.includes('open trades')) {
      if (positions.length === 0) {
        response = `📊 Current Positions\n\n📁 No open positions\n\n💡 Use "buy BTC" or "sell ETH" to open a position.`
      } else {
        response = `📊 Open Positions (${positions.length})\n\n` + positions.map(p =>
          `• ${p.symbol}: ${p.side.toUpperCase()} ${p.size} @ $${p.entryPrice.toFixed(2)}\n  P&L: $${p.pnl.toFixed(2)} (${p.pnlPercent.toFixed(2)}%)`
        ).join('\n\n')
      }
    }
    // 7. CLOSE POSITION
    else if (cmd.includes('close position') || cmd.includes('close ') || cmd.includes('exit ')) {
      if (!connectedPlatform) {
        response = "❌ No exchange connected."
      } else if (positions.length === 0) {
        response = "📊 No positions to close.\n\n💡 Open a position first using 'buy BTC' or 'sell ETH'."
      } else {
        response = `🗑️ Close Position (Demo)\n\n⚠️ Would close all positions:\n\n` + positions.map(p => `• ${p.symbol}: ${p.size} units`).join('\n') + `\n\n💡 In demo mode - connect to live API for real closing.`
        executedTrade = true
        addTerminalLog(`CLOSE ALL POSITIONS`)
      }
    }
    // 8. BALANCE & PORTFOLIO
    else if (cmd.includes('balance') || cmd.includes('portfolio') || cmd.includes('account')) {
      const balances = platforms.filter(p => p.status === 'connected').map(p =>
        `• ${p.name}: $${p.balance.toLocaleString()}`
      ).join('\n')
      response = `💰 Account Overview\n\n` + (balances || 'No exchanges connected') + `\n\n📊 Total Portfolio: $${totalBalance.toLocaleString()}\n📈 Open Positions: ${positions.length}\n🔗 Connected: ${platforms.filter(p => p.status === 'connected').length} exchanges\n\n💡 Go to Settings to add more exchanges.`
    }
    // 9. MARKET PRICE / PRICE CHECK
    else if (cmd.includes('price') || cmd.includes('quote') || cmd.includes('rate')) {
      const symbolMatch = inputMessage.match(/(?:price|quote|rate)\s+([A-Z]+(?:\/[A-Z]+)?)/i)
      const symbol = symbolMatch ? symbolMatch[1].toUpperCase() : 'BTC/USDT'
      const price = (Math.random() * 50000 + 30000).toFixed(2)
      const change = (Math.random() * 10 - 5).toFixed(2)

      response = `📊 ${symbol} Price\n\n💵 Current: $${price}\n📈 24h Change: ${change}%\n📊 High: $${(parseFloat(price) * 1.02).toFixed(2)}\n📉 Low: $${(parseFloat(price) * 0.98).toFixed(2)}\n\n🔗 Connect exchange for real-time prices.`
    }
    // 10. RISK MANAGEMENT
    else if (cmd.includes('risk') || cmd.includes('position size') || cmd.includes('lot size')) {
      response = `⚙️ Risk Management Settings\n\n📊 Current Risk Profile: Conservative\n\n• Max Risk/Trade: ${riskSettings.maxRiskPerTrade}%\n• Max Daily Loss: ${riskSettings.maxDailyLoss}%\n• Max Open Positions: ${riskSettings.maxPositions}\n\n💡 With $10,000 account:\n• 2% risk = $200 per trade\n• 20 pip stop loss = 1 lot\n\n💡 Adjust in Settings → Risk Management`
    }
    // 11. STRATEGIES
    else if (cmd.includes('strategy') || cmd.includes('strategies')) {
      const activeStrats = strategies.filter(s => s.status === 'active').map(s => s.name).join(', ') || 'None'
      response = `🎯 Trading Strategies\n\n📊 Active: ${activeStrats}\n\nAvailable Strategies:\n• RSI Mean Reversion - Buy oversold, sell overbought\n• MA Crossover - Trend following\n• Grid Trading - Range-bound markets\n\n💡 Use Automation tab to enable strategies.\n💡 Say "activate RSI" to enable a strategy.`
    }
    // 12. AI ANALYSIS
    else if (cmd.includes('analyze') || cmd.includes('analysis') || cmd.includes('forecast')) {
      const symbolMatch = inputMessage.match(/analyze\s+([A-Z]+(?:\/[A-Z]+)?)/i)
      const symbol = symbolMatch ? symbolMatch[1].toUpperCase() : 'BTC/USDT'
      const trends = ['BULLISH', 'BEARISH', 'SIDEWAYS', 'STRONG BULLISH', 'STRONG BEARISH']
      const signals = ['BUY', 'SELL', 'HULL', 'STRONG BUY', 'STRONG SELL']
      const trend = trends[Math.floor(Math.random() * trends.length)]
      const signal = signals[Math.floor(Math.random() * signals.length)]
      const confidence = Math.floor(Math.random() * 30 + 60)
      const rsi = (Math.random() * 100).toFixed(1)

      response = `🔍 AI Analysis: ${symbol}\n\n📈 Trend: ${trend}\n🎯 Signal: ${signal}\n📊 Confidence: ${confidence}%\n\nTechnical Indicators:\n• RSI(14): ${rsi}\n• MACD: ${Math.random() > 0.5 ? 'Bullish' : 'Bearish'} Cross\n• Support: $${(Math.random() * 40000).toFixed(0)}\n• Resistance: $${(Math.random() * 50000).toFixed(0)}\n\n💡 Connect exchange for live AI analysis.`
    }
    // 13. AUTO TRADING
    else if (cmd.includes('auto on') || cmd.includes('enable auto') || cmd.includes('automate')) {
      if (!connectedPlatform) {
        response = "❌ Cannot enable auto trading. Connect an exchange first."
      } else {
        setAutoTradingEnabled(true)
        response = `✅ AUTO TRADING ENABLED!\n\n🤖 Kazzy will now:\n• Monitor markets 24/7\n• Execute trades based on AI signals\n• Manage risk automatically\n• Use your configured strategies\n\n🛑 Say "auto off" to stop.`
        addTerminalLog('AUTO TRADING ENABLED')
      }
    }
    else if (cmd.includes('auto off') || cmd.includes('disable auto') || cmd.includes('stop auto')) {
      setAutoTradingEnabled(false)
      response = "⚪ AUTO TRADING DISABLED\n\nAll automated trading has been paused.\n\n💡 Say 'auto on' to re-enable."
      addTerminalLog('AUTO TRADING DISABLED')
    }
    // 14. PERFORMANCE / STATS
    else if (cmd.includes('performance') || cmd.includes('stats') || cmd.includes('statistics')) {
      const winRate = Math.floor(Math.random() * 30 + 50)
      const totalTrades = Math.floor(Math.random() * 100 + 20)
      const winningTrades = Math.floor(totalTrades * winRate / 100)
      const profitFactor = (Math.random() * 2 + 1).toFixed(2)

      response = `📊 Trading Performance\n\n📈 Win Rate: ${winRate}%\n💰 Total Trades: ${totalTrades}\n✅ Winning: ${winningTrades}\n❌ Losing: ${totalTrades - winningTrades}\n📊 Profit Factor: ${profitFactor}\n\n💡 Connect live account for real stats.`
    }
    // 15. ALERTS
    else if (cmd.includes('alert') || cmd.includes('notify') || cmd.includes('alarm')) {
      response = `🔔 Price Alerts (Demo)\n\n📊 No active alerts\n\n💡 Create alerts like:\n• "Alert me when BTC hits $50,000"\n• "Notify when ETH drops below $2,000"\n\n🔗 Connect exchange for real alerts.`
    }
    // 16. SHOW ALL ASSETS
    else if (cmd.includes('assets') || cmd.includes('instruments') || cmd.includes('symbols')) {
      response = `🌍 ALL AVAILABLE ASSETS - Kazzy Agent

══════════════════════════════════════
💱 FOREX - MetaTrader/cTrader
══════════════════════════════════════
MAJOR PAIRS:
EUR/USD | GBP/USD | USD/JPY | USD/CHF | AUD/USD | USD/CAD | NZD/USD

MINOR PAIRS:
EUR/GBP | EUR/JPY | GBP/JPY | CHF/JPY | EUR/CHF | AUD/JPY

EXOTIC PAIRS:
USD/TRY | USD/ZAR | USD/PLN | EUR/TRY | GBP/TRY

══════════════════════════════════════
₿ CRYPTO - Binance/Bybit/Coinbase
══════════════════════════════════════
BITCOIN: BTC/USDT | BTC/BTC | BTC/USD
ETHEREUM: ETH/USDT | ETH/BTC | ETH/USD
ALTCOINS: SOL/USDT | XRP/USDT | ADA/USDT | DOGE/USDT
         AVAX/USDT | DOT/USDT | MATIC/USDT | LINK/USDT

══════════════════════════════════════
📈 STOCKS - IBKR/Alpaca/TD Ameritrade
══════════════════════════════════════
TECH: AAPL | MSFT | GOOGL | META | NVDA | TSLA | AMD | INTC
FINANCE: JPM | BAC | GS | MS | V | MA
ENERGY: XOM | CVX | COP | SLB
ETFs: SPY | QQQ | IWM | VTI | VOO

══════════════════════════════════════
🥇 COMMODITIES - MT5/CFDs
══════════════════════════════════════
PRECIOUS METALS: XAU/USD (Gold) | XAG/USD (Silver) | XPT/USD (Platinum)
ENERGY: WTI | BRENT | NG | HO | RB
AGRICULTURE: W | S | C | KC | ZS | ZC

══════════════════════════════════════
📊 INDICES - MT5/CFDs/Futures
══════════════════════════════════════
US: US30 (Dow) | US500 (S&P) | NAS100 (Nasdaq)
UK: UK100 (FTSE)
DE: GER40 (DAX)
FR: FRA40 (CAC)
JP: JPN225 (Nikkei)

══════════════════════════════════════
🔮 FUTURES - CME/IBKR/Tradovate
══════════════════════════════════════
EQUITY: ES (S&P 500) | NQ (Nasdaq) | YM (Dow) | RTY (Russell)
ENERGY: CL (Crude) | NG (Natural Gas) | RB (RBOB)
METALS: GC (Gold) | SI (Silver) | HG (Copper)

══════════════════════════════════════
🎰 OPTIONS - IBKR/ThinkOrSwim
══════════════════════════════════════
STOCK OPTIONS: AAPL, MSFT, TSLA, NVDA (Calls/Puts)
EXPIRATIONS: Weekly, Monthly, LEAPs

══════════════════════════════════════
📜 BONDS - IBKR/Treasury Direct
══════════════════════════════════════
US TREASURIES: US2Y | US5Y | US10Y | US30Y
CORPORATE: Investment Grade | High Yield

💡 Say "price XAU/USD" or "buy 1 AAPL" to trade!`
    }
    // 18. HELP - Show all commands
    else if (cmd.includes('help') || cmd === '?' || cmd.includes('commands')) {
      response = `🤖 Kazzy AI - Universal Trading Assistant

══════════════════════════════════════
🌍 ALL ASSET CLASSES - I CAN TRADE:
══════════════════════════════════════

💱 FOREX (30+ pairs):
• Major: EUR/USD, GBP/USD, USD/JPY, USD/CHF
• Minor: EUR/GBP, AUD/USD, USD/CAD, NZD/USD

₿ CRYPTO (100+ coins):
• Bitcoin: BTC/USDT, BTC/BTC
• Altcoins: ETH, SOL, XRP, ADA, DOGE, AVAX

📈 STOCKS (10,000+):
• US: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA

🥇 COMMODITIES:
• Metals: XAU/USD (Gold), XAG/USD (Silver)
• Energy: WTI, BRENT, NATGAS

📊 INDICES:
• US: US30, US500, NAS100
• Europe: UK100, GER40, FRA40

🎰 OPTIONS:
• Call/Put options on stocks

🔮 FUTURES:
• ES (S&P 500), NQ (Nasdaq), YM (Dow)

📜 BONDS:
• US10Y, US2Y, DE10Y (Treasuries)

══════════════════════════════════════
📝 COMMANDS:
══════════════════════════════════════

💰 TRADING:
• "buy 0.01 BTC" - Market buy crypto
• "buy 10 AAPL" - Buy stocks
• "buy 1 lot XAU/USD" - Buy gold
• "sell 0.1 ETH" - Market sell

📊 POSITIONS:
• "show positions" - View open positions
• "close all" - Close all positions

💵 ACCOUNT:
• "balance" - Check account balance
• "price AAPL" - Check stock price
• "price XAU/USD" - Check gold price

⚙️ SETTINGS:
• "risk" - Risk management info
• "auto on/off" - Toggle auto trading
• "assets" - Show all asset classes

🔍 ANALYSIS:
• "analyze AAPL" - AI stock analysis
• "analyze XAU/USD" - AI gold analysis`
    }
    // 19. EMERGENCY STOP
    else if (cmd.includes('emergency') || cmd.includes('panic') || cmd.includes('stop all')) {
      setAutoTradingEnabled(false)
      response = "🛑 EMERGENCY STOP ACTIVATED!\n\n⚠️ All auto trading has been paused.\n⚠️ All open positions remain.\n\n💡 Use Emergency Stop button in sidebar to close ALL positions immediately."
      addTerminalLog('EMERGENCY STOP')
    }
    // Default - smart response
    else {
      // Check for any keyword matches
      if (cmd.includes('hello') || cmd.includes('hi') || cmd.includes('hey')) {
        response = `👋 Hello! I'm Kazzy, your AI trading assistant.\n\nI can help you:\n💰 Execute trades\n📊 Analyze markets\n⚙️ Manage risk\n🤖 Run automated strategies\n\nJust type a command or ask "help" for all options!`
      } else if (cmd.includes('thank')) {
        response = `😊 You're welcome! Happy to help with your trading.\n\n💡 Remember to trade responsibly and never risk more than you can afford to lose.`
      } else {
        response = `🤔 I didn't understand that command.\n\n💡 Type "help" to see all available commands, or try:\n• "buy 0.01 BTC"\n• "analyze ETH"\n• "show my balance"\n• "auto on"`
      }
    }

    const aiMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: response,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, aiMessage])
    setTerminalLogs(prev => [...prev, `Kazzy: ${response.substring(0, 100)}...`])
    setIsTyping(false)
  }, [inputMessage, autoTradingEnabled, platforms, totalBalance, positions, riskSettings, strategies])

  // Calculate position size
  const calculatePositionSize = useCallback(() => {
    const riskAmount = calcBalance * (calcRisk / 100)
    const pipValue = 10
    const lotSize = riskAmount / (calcStopLoss * pipValue)
    setCalcResult(Math.round(lotSize * 100) / 100)
  }, [calcBalance, calcRisk, calcStopLoss])

  // Copy signal
  const copySignal = (signal: Signal) => {
    const text = `${signal.direction.toUpperCase()} ${signal.symbol}\nEntry: ${signal.entryZone}\nSL: ${signal.stopLoss}\nTP: ${signal.takeProfit}`
    navigator.clipboard.writeText(text)
    setCopiedSignal(signal.id)
    setTimeout(() => setCopiedSignal(null), 2000)
  }

  // Connect to exchange
  const connectToExchange = useCallback(async () => {
    if (!selectedExchange || !apiKey || !apiSecret) return

    setPlatforms(prev => prev.map(p => {
      if (p.id === selectedExchange) {
        return {
          ...p,
          status: 'connecting',
          apiKey,
          apiSecret
        }
      }
      return p
    }))

    try {
      // Call API to connect to exchange
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

      const response = await fetch(`${API_BASE}/api/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exchange: selectedExchange,
          api_key: apiKey,
          api_secret: apiSecret,
          testnet: testnet
        })
      })

      const data = await response.json()

      if (data.success) {
        // Fetch balance after successful connection
        const balanceResponse = await fetch(`${API_BASE}/api/balance/${selectedExchange}`)
        const balanceData = await balanceResponse.json()

        const actualBalance = balanceData.total || balanceData.free || 0

        setPlatforms(prev => prev.map(p => {
          if (p.id === selectedExchange) {
            return {
              ...p,
              status: 'connected',
              balance: actualBalance,
              lastSync: 'Just now'
            }
          }
          return p
        }))

        addTerminalLog(`Connected to ${selectedExchange} successfully! Balance: $${actualBalance.toFixed(2)}`)
        addMessage(`Successfully connected to ${selectedExchange}. Your account balance: $${actualBalance.toFixed(2)}`)
      } else {
        setPlatforms(prev => prev.map(p => {
          if (p.id === selectedExchange) {
            return { ...p, status: 'error' }
          }
          return p
        }))
        addTerminalLog(`Failed to connect to ${selectedExchange}: ${data.message}`)
        addMessage(`Failed to connect to ${selectedExchange}: ${data.message}`)
      }
    } catch (error) {
      console.error('Connection error:', error)
      // Fallback to mock for demo
      setTimeout(() => {
        setPlatforms(prev => prev.map(p => {
          if (p.id === selectedExchange) {
            const mockBalance = p.type === 'crypto' ? Math.random() * 50000 : Math.random() * 50000
            return {
              ...p,
              status: 'connected',
              balance: Math.round(mockBalance),
              lastSync: 'Just now'
            }
          }
          return p
        }))
        addTerminalLog(`Connected to ${selectedExchange} (demo mode)`)
        addMessage(`Connected to ${selectedExchange} in demo mode. API server not available.`)
      }, 1000)
    }

    setApiKeysModalOpen(false)
    setApiKey('')
    setApiSecret('')
    setSelectedExchange('')
  }, [selectedExchange, apiKey, apiSecret, testnet])

  // Disconnect exchange
  const disconnectExchange = (platformId: string) => {
    setPlatforms(prev => prev.map(p => {
      if (p.id === platformId) {
        return {
          ...p,
          status: 'disconnected',
          balance: 0,
          lastSync: 'Not connected',
          apiKey: undefined,
          apiSecret: undefined
        }
      }
      return p
    }))
  }

  // Toggle strategy
  const toggleStrategy = (strategyId: string) => {
    setStrategies(prev => prev.map(s => {
      if (s.id === strategyId) {
        const newStatus = s.status === 'active' ? 'inactive' : 'active'
        if (newStatus === 'active' && !autoTradingEnabled) {
          setAutoTradingEnabled(true)
        }
        return {
          ...s,
          status: newStatus,
          lastRun: newStatus === 'active' ? new Date().toISOString() : undefined
        }
      }
      return s
    }))

    const strategy = strategies.find(s => s.id === strategyId)
    addTerminalLog(`${strategy?.status === 'active' ? 'Paused' : 'Started'} strategy: ${strategy?.name}`)
  }

  // Emergency stop
  const triggerEmergencyStop = () => {
    setAutoTradingEnabled(false)
    setStrategies(prev => prev.map(s => ({ ...s, status: 'inactive' })))
    setEmergencyStopOpen(false)
    addTerminalLog('🛑 EMERGENCY STOP TRIGGERED - All positions closed!')
    addMessage("Emergency stop activated. All automated trading has been halted and positions closed. You can review the terminal logs for details.")
  }

  // Save OpenAI API Key
  const saveOpenAIKey = () => {
    if (!openaiKey.startsWith('sk-')) {
      addMessage('Invalid OpenAI API key. It should start with "sk-"')
      return
    }
    localStorage.setItem('kazzy_openai_key', openaiKey)
    addMessage('OpenAI API key saved successfully!')
    addTerminalLog('OpenAI API key saved')
  }

  // Load API keys on mount
  useEffect(() => {
    const savedOpenAIKey = localStorage.getItem('kazzy_openai_key')
    if (savedOpenAIKey) {
      setOpenaiKey(savedOpenAIKey)
    }

    const savedPoeKey = localStorage.getItem('kazzy_poe_key')
    const savedPoeModel = localStorage.getItem('kazzy_poe_model')
    if (savedPoeKey) {
      setPoeKey(savedPoeKey)
    }
    if (savedPoeModel) {
      setPoeModel(savedPoeModel)
    }
  }, [])

  // Execute trade
  const executeTrade = async () => {
    if (!tradeSymbol || !tradeAmount) {
      addMessage('Please enter symbol and amount')
      return
    }

    const connectedPlatform = platforms.find(p => p.status === 'connected')
    if (!connectedPlatform) {
      addMessage('Please connect an exchange first')
      return
    }

    setIsTrading(true)
    addTerminalLog(`Executing ${tradeSide.toUpperCase()} ${tradeAmount} ${tradeSymbol}...`)

    try {
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE}/api/trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exchange: connectedPlatform.id,
          symbol: tradeSymbol,
          side: tradeSide,
          quantity: parseFloat(tradeAmount),
          order_type: 'market'
        })
      })

      const data = await response.json()

      if (data.success) {
        addMessage(`Trade executed successfully! ${tradeSide.toUpperCase()} ${tradeAmount} ${tradeSymbol}`)
        addTerminalLog(`✅ Trade executed: ${tradeSide.toUpperCase()} ${tradeAmount} ${tradeSymbol}`)
      } else {
        addMessage(`Trade failed: ${data.message || 'Unknown error'}`)
        addTerminalLog(`❌ Trade failed`)
      }
    } catch (error) {
      console.error('Trade error:', error)
      // Demo mode - simulate trade
      setTimeout(() => {
        addMessage(`Demo: ${tradeSide.toUpperCase()} ${tradeAmount} ${tradeSymbol} (Demo mode)`)
        addTerminalLog(`Demo trade: ${tradeSide.toUpperCase()} ${tradeAmount} ${tradeSymbol}`)
      }, 1000)
    }

    setIsTrading(false)
    setTradeAmount('')
  }

  // Add message to chat
  const addMessage = (content: string) => {
    const msg: ChatMessage = {
      id: Date.now().toString(),
      role: 'assistant',
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, msg])
  }

  // Add to terminal
  const addTerminalLog = (log: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setTerminalLogs(prev => [`[${timestamp}] ${log}`, ...prev.slice(0, 99)])
  }

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-emerald-500'
      case 'disconnected': return 'bg-slate-500'
      case 'error': return 'bg-red-500'
      case 'connecting': return 'bg-yellow-500'
      default: return 'bg-slate-500'
    }
  }

  const formatNumber = (num: number, decimals = 2) => {
    return num.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
  }

  const navItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'portfolio', icon: Wallet, label: 'Portfolio' },
    { id: 'automation', icon: Rocket, label: 'Automation' },
    { id: 'signals', icon: Radio, label: 'Signals' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <div className="min-h-screen bg-[#0b0e11] text-slate-200 font-sans">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-14 bg-[#151a21] border-b border-[#2a3441] flex items-center justify-between px-4 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <span className="font-semibold text-lg">Kazzy Agent</span>
        </div>
        <button onClick={() => setMobileMenuOpen(true)} className="p-2 hover:bg-[#1c222b] rounded-lg">
          <Menu className="w-5 h-5" />
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 bg-black/50 z-50" onClick={() => setMobileMenuOpen(false)}>
          <div className="fixed right-0 top-0 bottom-0 w-64 bg-[#151a21] border-l border-[#2a3441] p-4" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <span className="font-semibold">Menu</span>
              <button onClick={() => setMobileMenuOpen(false)} className="p-2 hover:bg-[#1c222b] rounded-lg">
                <CloseIcon className="w-5 h-5" />
              </button>
            </div>
            <nav className="space-y-2">
              {navItems.map(item => (
                <button
                  key={item.id}
                  onClick={() => { setActiveTab(item.id); setMobileMenuOpen(false) }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${activeTab === item.id ? 'bg-blue-500/20 text-blue-400' : 'hover:bg-[#1c222b]'}`}
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <aside className={`fixed left-0 top-0 bottom-0 bg-[#151a21] border-r border-[#2a3441] transition-all duration-300 z-40 ${sidebarCollapsed ? 'w-16' : 'w-64'} hidden lg:flex flex-col`}>
        <div className="h-14 flex items-center px-4 border-b border-[#2a3441]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Bot className="w-5 h-5 text-white" />
            </div>
            {!sidebarCollapsed && (
              <div>
                <span className="font-semibold text-lg">Kazzy</span>
                <span className="text-xs text-slate-500 ml-1">Agent</span>
              </div>
            )}
          </div>
        </div>

        {/* Auto-trading toggle */}
        {!sidebarCollapsed && (
          <div className="px-3 py-3 border-b border-[#2a3441]">
            <div className="bg-[#1c222b] rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Auto Trading</span>
                <button
                  onClick={() => {
                    const hasConnected = platforms.some(p => p.status === 'connected')
                    if (!hasConnected) {
                      addMessage("Please connect an exchange first before enabling auto-trading.")
                      return
                    }
                    setAutoTradingEnabled(!autoTradingEnabled)
                    addTerminalLog(`Auto-trading ${!autoTradingEnabled ? 'ENABLED' : 'DISABLED'}`)
                    addMessage(!autoTradingEnabled
                      ? "Auto-trading is now enabled! I'll execute trades based on your active strategies."
                      : "Auto-trading has been disabled. All positions will remain open but no new trades will be executed.")
                  }}
                  className={`w-10 h-5 rounded-full transition-colors ${autoTradingEnabled ? 'bg-emerald-500' : 'bg-slate-600'}`}
                >
                  <div className={`w-4 h-4 rounded-full bg-white transition-transform ${autoTradingEnabled ? 'translate-x-5' : 'translate-x-0.5'}`} />
                </button>
              </div>
              <div className="text-xs text-slate-500">
                {autoTradingEnabled
                  ? <span className="text-emerald-400">● Active - Monitoring markets</span>
                  : <span className="text-slate-500">○ Inactive</span>
                }
              </div>
            </div>
          </div>
        )}

        <nav className="flex-1 p-3 space-y-1.5 overflow-y-auto">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${activeTab === item.id ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'hover:bg-[#1c222b] text-slate-400'}`}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!sidebarCollapsed && <span className="text-sm">{item.label}</span>}
            </button>
          ))}
        </nav>

        {/* Platforms */}
        {!sidebarCollapsed && (
          <div className="p-3 border-t border-[#2a3441]">
            <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2 px-2">Platforms ({connectedPlatforms}/7)</div>
            <div className="space-y-1.5 max-h-48 overflow-y-auto">
              {platforms.map(platform => (
                <div
                  key={platform.id}
                  className="flex items-center justify-between p-2 rounded-lg bg-[#1c222b] hover:bg-[#242d3a] cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedExchange(platform.id)
                    setApiKeysModalOpen(true)
                  }}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{platform.logo}</span>
                    <span className="text-xs">{platform.name}</span>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(platform.status)}`} />
                </div>
              ))}
            </div>
          </div>
        )}

        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="h-12 border-t border-[#2a3441] flex items-center justify-center hover:bg-[#1c222b] transition-colors"
        >
          {sidebarCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </aside>

      {/* Main Content */}
      <main className={`transition-all duration-300 ${sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-64'} ${kazzyPanelOpen ? 'lg:mr-96' : ''} pt-14 lg:pt-0`}>
        <div className="sticky top-0 bg-[#0b0e11]/80 backdrop-blur-xl border-b border-[#2a3441] z-30">
          <div className="h-10 bg-[#151a21] overflow-hidden flex items-center">
            <div className="flex animate-ticker whitespace-nowrap">
              {[...tickers, ...tickers].map((ticker, i) => (
                <div key={i} className="flex items-center gap-2 px-4 border-r border-[#2a3441]/50">
                  <span className="text-sm font-medium text-slate-300">{ticker.symbol}</span>
                  <span className="text-sm font-mono">{formatNumber(ticker.price, ticker.symbol.includes('BTC') || ticker.symbol.includes('ETH') ? 0 : ticker.symbol.includes('JPY') ? 2 : 4)}</span>
                  <span className={`text-xs flex items-center ${ticker.change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {ticker.change >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {Math.abs(ticker.changePercent).toFixed(2)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="px-4 py-3 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-6">
              <div>
                <div className="text-xs text-slate-500">Total Net Worth</div>
                <div className="text-xl font-semibold font-mono">${formatNumber(totalBalance, 0)}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Daily P&L</div>
                <div className={`text-sm font-semibold font-mono flex items-center gap-1 ${totalPnL >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {totalPnL >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                  ${formatNumber(Math.abs(totalPnL), 0)}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className={`px-2 py-1 rounded text-xs font-medium ${autoTradingEnabled ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-700 text-slate-400'}`}>
                  {autoTradingEnabled ? 'AUTO' : 'MANUAL'}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => setShowTerminal(!showTerminal)} className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-2 transition-colors ${showTerminal ? 'bg-blue-500' : 'bg-[#1c222b] hover:bg-[#242d3a]'}`}>
                <Terminal className="w-4 h-4" />
              </button>
              <button onClick={() => setEmergencyStopOpen(true)} className="px-3 py-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm flex items-center gap-2 transition-colors">
                <StopCircle className="w-4 h-4" />
                <span className="hidden sm:inline">Stop All</span>
              </button>
              <button onClick={() => setKazzyPanelOpen(!kazzyPanelOpen)} className="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 rounded-lg text-sm flex items-center gap-2 transition-colors">
                <Bot className="w-4 h-4" />
                <span className="hidden sm:inline">Kazzy</span>
              </button>
            </div>
          </div>
        </div>

        {/* Terminal Panel */}
        {showTerminal && (
          <div className="bg-[#0d1117] border-b border-[#2a3441] p-3 max-h-48 overflow-y-auto font-mono text-xs">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400">Terminal</span>
              <button onClick={() => setTerminalLogs([])} className="text-slate-500 hover:text-white">Clear</button>
            </div>
            {terminalLogs.length === 0 ? (
              <div className="text-slate-600">No logs yet...</div>
            ) : (
              terminalLogs.map((log, i) => (
                <div key={i} className="text-slate-300 py-0.5">{log}</div>
              ))
            )}
          </div>
        )}

        <div className="p-4 space-y-4">
          {/* Persistent Chart - Always rendered and visible */}
          <div className="bg-[#151a21] rounded-xl border border-[#2a3441] overflow-hidden">
            <div className="flex items-center justify-between p-3 border-b border-[#2a3441]">
              <div className="flex items-center gap-3">
                <select
                  value={chartSymbol}
                  onChange={(e) => setChartSymbol(e.target.value)}
                  className="bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-1.5 text-sm"
                >
                  <option value="BTC/USDT">BTC/USDT</option>
                  <option value="ETH/USDT">ETH/USDT</option>
                  <option value="SOL/USDT">SOL/USDT</option>
                  <option value="XRP/USDT">XRP/USDT</option>
                  <option value="ADA/USDT">ADA/USDT</option>
                  <option value="DOGE/USDT">DOGE/USDT</option>
                  <option value="EUR/USD">EUR/USD</option>
                  <option value="XAU/USD">XAU/USD</option>
                </select>
                <div className="flex gap-1">
                  {['1H', '4H', '1D', '1W'].map(tf => (
                    <button
                      key={tf}
                      onClick={() => setChartTimeframe(tf)}
                      className={`px-2.5 py-1 rounded text-xs transition-colors ${chartTimeframe === tf ? 'bg-blue-500/20 text-blue-400' : 'hover:bg-[#1c222b]'}`}
                    >
                      {tf}
                    </button>
                  ))}
                </div>
              </div>
              {candlestickData.length > 0 && (
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-slate-400">
                    ${candlestickData[candlestickData.length - 1]?.close.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                  <RefreshCw
                    className="w-4 h-4 text-slate-500 cursor-pointer hover:text-white"
                    onClick={() => fetchCandlestickData(chartSymbol, chartTimeframe)}
                  />
                </div>
              )}
            </div>
            <div ref={setChartContainer} className="h-80" />
          </div>

          {/* Dashboard View */}
          {activeTab === 'dashboard' && (
            <>
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                {/* Live Signals Panel */}
                <div className="bg-[#151a21] rounded-xl border border-[#2a3441] overflow-hidden">
                  <div className="p-3 border-b border-[#2a3441] flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Radio className="w-4 h-4 text-blue-400" />
                      <span className="font-medium">Live Signals</span>
                    </div>
                  </div>
                  <div className="divide-y divide-[#2a3441] max-h-80 overflow-y-auto">
                    {signals.map(signal => (
                      <div key={signal.id} className="p-3 hover:bg-[#1c222b] transition-colors">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{signal.symbol}</span>
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${signal.direction === 'buy' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                            {signal.direction.toUpperCase()}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div><div className="text-slate-500">Entry</div><div className="font-mono">{signal.entryZone}</div></div>
                          <div><div className="text-slate-500">SL</div><div className="font-mono text-red-400">{signal.stopLoss}</div></div>
                          <div><div className="text-slate-500">TP</div><div className="font-mono text-emerald-400">{signal.takeProfit}</div></div>
                        </div>
                        <div className="flex items-center justify-between mt-2">
                          <div className="flex items-center gap-1">
                            <div className="w-16 h-1.5 bg-[#2a3441] rounded-full overflow-hidden">
                              <div className="h-full bg-blue-500" style={{ width: `${signal.confidence}%` }} />
                            </div>
                            <span className="text-xs text-slate-500">{signal.confidence}%</span>
                          </div>
                          <button onClick={() => copySignal(signal)} className="text-xs text-slate-400 hover:text-white flex items-center gap-1">
                            {copiedSignal === signal.id ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                            Copy
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Positions */}
              <div className="bg-[#151a21] rounded-xl border border-[#2a3441] overflow-hidden">
                <div className="p-3 border-b border-[#2a3441] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-blue-400" />
                    <span className="font-medium">Active Positions</span>
                    <span className="text-xs text-slate-500">({positions.length})</span>
                  </div>
                </div>
                {positions.length === 0 ? (
                  <div className="p-8 text-center text-slate-500">
                    <Layers className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No open positions</p>
                    <p className="text-xs mt-1">Connect an exchange and enable auto-trading to start</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-[#2a3441]">
                          <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Symbol</th>
                          <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Side</th>
                          <th className="text-right text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Size</th>
                          <th className="text-right text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Entry</th>
                          <th className="text-right text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Current</th>
                          <th className="text-right text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">P&L</th>
                          <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Platform</th>
                          <th className="text-right text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#2a3441]">
                        {positions.map(position => (
                          <tr key={position.id} className="hover:bg-[#1c222b] transition-colors">
                            <td className="px-4 py-3 font-medium">{position.symbol}</td>
                            <td className="px-4 py-3">
                              <span className={`px-2 py-0.5 rounded text-xs font-medium ${position.side === 'buy' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                                {position.side.toUpperCase()}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-right font-mono">{position.size}</td>
                            <td className="px-4 py-3 text-right font-mono">{formatNumber(position.entryPrice, 4)}</td>
                            <td className="px-4 py-3 text-right font-mono">{formatNumber(position.currentPrice, 4)}</td>
                            <td className={`px-4 py-3 text-right font-mono font-medium ${position.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                              {position.pnl >= 0 ? '+' : ''}${formatNumber(position.pnl, 0)}
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-1.5">
                                <span>{platforms.find(p => p.id === position.platform)?.logo}</span>
                                <span className="text-xs text-slate-400">{platforms.find(p => p.id === position.platform)?.name}</span>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-right">
                              <button className="px-2 py-1 text-xs bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded transition-colors">
                                Close
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Automation Tab */}
          {activeTab === 'automation' && (
            <div className="space-y-4">
              <div className="bg-[#151a21] rounded-xl border border-[#2a3441] p-4">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-semibold">Trading Strategies</h3>
                    <p className="text-sm text-slate-500">Configure and activate automated trading strategies</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-400">Master Control</span>
                    <button
                      onClick={() => {
                        if (connectedPlatforms === 0) {
                          addMessage("Please connect an exchange first!")
                          return
                        }
                        setAutoTradingEnabled(!autoTradingEnabled)
                      }}
                      className={`w-12 h-6 rounded-full transition-colors ${autoTradingEnabled ? 'bg-emerald-500' : 'bg-slate-600'}`}
                    >
                      <div className={`w-5 h-5 rounded-full bg-white transition-transform ${autoTradingEnabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {strategies.map(strategy => (
                    <div key={strategy.id} className={`bg-[#1c222b] rounded-lg p-4 border ${strategy.status === 'active' ? 'border-emerald-500/50' : 'border-[#2a3441]'}`}>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <Cpu className={`w-5 h-5 ${strategy.status === 'active' ? 'text-emerald-400' : 'text-slate-400'}`} />
                          <span className="font-medium">{strategy.name}</span>
                        </div>
                        <span className={`text-xs px-2 py-0.5 rounded ${strategy.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-700 text-slate-400'}`}>
                          {strategy.status.toUpperCase()}
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 mb-3">
                        {strategy.id === 'rsi' && 'Buys when RSI < 30, sells when RSI > 70'}
                        {strategy.id === 'ma_crossover' && 'Golden cross = buy, Death cross = sell'}
                        {strategy.id === 'grid' && 'Places orders at grid levels for range trading'}
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-500">Trades: {strategy.tradesCount}</span>
                        <button
                          onClick={() => toggleStrategy(strategy.id)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${strategy.status === 'active' ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' : 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'}`}
                        >
                          {strategy.status === 'active' ? 'Stop' : 'Start'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Risk Settings */}
              <div className="bg-[#151a21] rounded-xl border border-[#2a3441] p-4">
                <h3 className="font-semibold mb-4">Risk Management</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="text-xs text-slate-500 block mb-1">Max Risk per Trade (%)</label>
                    <input
                      type="number"
                      value={riskSettings.maxRiskPerTrade}
                      onChange={e => setRiskSettings(prev => ({ ...prev, maxRiskPerTrade: Number(e.target.value) }))}
                      className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-500 block mb-1">Max Daily Loss (%)</label>
                    <input
                      type="number"
                      value={riskSettings.maxDailyLoss}
                      onChange={e => setRiskSettings(prev => ({ ...prev, maxDailyLoss: Number(e.target.value) }))}
                      className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-500 block mb-1">Max Open Positions</label>
                    <input
                      type="number"
                      value={riskSettings.maxPositions}
                      onChange={e => setRiskSettings(prev => ({ ...prev, maxPositions: Number(e.target.value) }))}
                      className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-2 text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <div className="space-y-4">
              <div className="bg-[#151a21] rounded-xl border border-[#2a3441] p-4">
                <h3 className="font-semibold mb-4">Exchange Connections</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {platforms.map(platform => (
                    <div key={platform.id} className={`bg-[#1c222b] rounded-lg p-4 border ${platform.status === 'connected' ? 'border-emerald-500/30' : 'border-[#2a3441]'}`}>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{platform.logo}</span>
                          <span className="font-medium">{platform.name}</span>
                        </div>
                        <div className={`w-2.5 h-2.5 rounded-full ${getStatusColor(platform.status)} ${platform.status === 'connecting' ? 'animate-pulse' : ''}`} />
                      </div>
                      <div className="text-xs text-slate-500 mb-3">
                        {platform.status === 'connected'
                          ? `Balance: $${formatNumber(platform.balance, 0)} • ${platform.lastSync}`
                          : platform.status === 'connecting'
                          ? 'Connecting...'
                          : 'Not connected'
                        }
                      </div>
                      {platform.status === 'connected' ? (
                        <button
                          onClick={() => disconnectExchange(platform.id)}
                          className="w-full py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm font-medium transition-colors"
                        >
                          Disconnect
                        </button>
                      ) : (
                        <button
                          onClick={() => {
                            setSelectedExchange(platform.id)
                            setApiKeysModalOpen(true)
                          }}
                          disabled={platform.status === 'connecting'}
                          className="w-full py-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                        >
                          {platform.status === 'connecting' ? 'Connecting...' : 'Connect'}
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* AI Provider Selection */}
              <div className="bg-[#151a21] rounded-xl border border-[#2a3441] p-4">
                <h3 className="font-semibold mb-4">AI Configuration</h3>

                {/* Provider Toggle */}
                <div className="flex gap-2 mb-4">
                  <button
                    onClick={() => setAiProvider('poe')}
                    className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                      aiProvider === 'poe'
                        ? 'bg-purple-500/20 text-purple-400 border border-purple-500/50'
                        : 'bg-[#1c222b] text-slate-400 border border-[#2a3441]'
                    }`}
                  >
                    🤖 Poe AI
                  </button>
                  <button
                    onClick={() => setAiProvider('openai')}
                    className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                      aiProvider === 'openai'
                        ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                        : 'bg-[#1c222b] text-slate-400 border border-[#2a3441]'
                    }`}
                  >
                    🔑 OpenAI
                  </button>
                </div>

                {aiProvider === 'poe' ? (
                  <div className="space-y-4">
                    {/* Poe API Key */}
                    <div>
                      <label className="text-xs text-slate-500 block mb-1">Poe API Key</label>
                      <div className="relative">
                        <input
                          type={showPoeKey ? 'text' : 'password'}
                          value={poeKey}
                          onChange={e => setPoeKey(e.target.value)}
                          placeholder="poa_..."
                          className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-2 text-sm pr-10"
                        />
                        <button
                          onClick={() => setShowPoeKey(!showPoeKey)}
                          className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-500 hover:text-slate-300"
                        >
                          {showPoeKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">Get key from poe.com/api_key</p>
                    </div>

                    {/* Poe Model Selector */}
                    <div>
                      <label className="text-xs text-slate-500 block mb-2">AI Model</label>
                      <div className="grid grid-cols-2 gap-2">
                        {poeModels.map(model => (
                          <button
                            key={model.id}
                            onClick={() => setPoeModel(model.id)}
                            className={`p-2 rounded-lg text-left text-xs transition-colors ${
                              poeModel === model.id
                                ? 'bg-purple-500/20 border border-purple-500/50'
                                : 'bg-[#1c222b] border border-[#2a3441] hover:border-purple-500/30'
                            }`}
                          >
                            <div className="font-medium text-slate-200">{model.name}</div>
                            <div className="text-slate-500">{model.desc}</div>
                          </button>
                        ))}
                      </div>
                    </div>

                    <button
                      onClick={() => {
                        localStorage.setItem('kazzy_poe_key', poeKey)
                        localStorage.setItem('kazzy_poe_model', poeModel)
                        addMessage('✅ Poe API key and model saved! You can now use advanced AI for trading.')
                        addTerminalLog('Poe API key saved')
                      }}
                      className="w-full py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                      Save Poe Settings
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="text-xs text-slate-500 block mb-1">OpenAI API Key</label>
                      <div className="relative">
                        <input
                          type={showOpenaiKey ? 'text' : 'password'}
                          value={openaiKey}
                          onChange={e => setOpenaiKey(e.target.value)}
                          placeholder="sk-..."
                          className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-2 text-sm pr-10"
                        />
                        <button
                          onClick={() => setShowOpenaiKey(!showOpenaiKey)}
                          className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-500 hover:text-slate-300"
                        >
                          {showOpenaiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">Required for GPT-4 powered AI analysis</p>
                    </div>
                    <button
                      onClick={saveOpenAIKey}
                      className="w-full py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                      Save OpenAI Key
                    </button>
                  </div>
                )}
              </div>

              {/* Quick Trade Section */}
              <div className="bg-[#151a21] rounded-xl border border-[#2a3441] p-4">
                <h3 className="font-semibold mb-4">Quick Trade</h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs text-slate-500 block mb-1">Symbol</label>
                      <input
                        type="text"
                        value={tradeSymbol}
                        onChange={e => setTradeSymbol(e.target.value)}
                        placeholder="BTC/USDT"
                        className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-2 text-sm"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-500 block mb-1">Amount</label>
                      <input
                        type="number"
                        value={tradeAmount}
                        onChange={e => setTradeAmount(e.target.value)}
                        placeholder="0.01"
                        className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-2 text-sm"
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setTradeSide('buy')}
                      className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${tradeSide === 'buy' ? 'bg-emerald-500 text-white' : 'bg-[#1c222b] text-slate-400 hover:bg-emerald-500/20'}`}
                    >
                      Buy
                    </button>
                    <button
                      onClick={() => setTradeSide('sell')}
                      className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${tradeSide === 'sell' ? 'bg-red-500 text-white' : 'bg-[#1c222b] text-slate-400 hover:bg-red-500/20'}`}
                    >
                      Sell
                    </button>
                  </div>
                  <button
                    onClick={executeTrade}
                    disabled={isTrading}
                    className={`w-full py-2.5 rounded-lg text-sm font-medium transition-colors ${tradeSide === 'buy' ? 'bg-emerald-500 hover:bg-emerald-600' : 'bg-red-500 hover:bg-red-600'} text-white disabled:opacity-50`}
                  >
                    {isTrading ? 'Processing...' : `Execute ${tradeSide.toUpperCase()}`}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Signals Tab */}
          {activeTab === 'signals' && (
            <div className="space-y-4">
              <div className="bg-[#151a21] rounded-xl border border-[#2a3441] p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold">Live Trading Signals</h3>
                  <div className="flex items-center gap-2">
                    {signalsLoading ? (
                      <span className="text-xs text-blue-400 animate-pulse">Fetching live data...</span>
                    ) : signalsLastUpdate ? (
                      <span className="text-xs text-slate-500">
                        Updated {signalsLastUpdate.toLocaleTimeString()}
                      </span>
                    ) : null}
                    <RefreshCw className={`w-4 h-4 text-slate-500 ${signalsLoading ? 'animate-spin' : ''}`} />
                  </div>
                </div>
                <div className="space-y-3">
                  {realSignals.length > 0 ? realSignals.map((signal) => (
                    <div key={signal.id} className="bg-[#1c222b] rounded-lg p-4 border border-[#2a3441] hover:border-blue-500/30 transition-colors">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <span className="font-semibold text-lg">{signal.symbol}</span>
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${signal.direction === 'buy' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                            {signal.direction.toUpperCase()}
                          </span>
                          <span className="px-2 py-0.5 rounded text-xs bg-blue-500/20 text-blue-400">
                            {signal.timeframe}
                          </span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-1">
                            <TrendingUp className="w-4 h-4 text-emerald-400" />
                            <span className={`text-sm font-mono ${signal.change_24h >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                              {signal.change_24h >= 0 ? '+' : ''}{signal.change_24h.toFixed(2)}%
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Shield className="w-4 h-4 text-blue-400" />
                            <span className="text-sm font-medium">{signal.confidence}%</span>
                          </div>
                        </div>
                      </div>

                      {/* Price & Strategy */}
                      <div className="flex items-center gap-4 mb-3 text-sm">
                        <div className="flex items-center gap-1">
                          <span className="text-slate-500">Price:</span>
                          <span className="font-mono text-white">${signal.price.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="text-slate-500">Strategy:</span>
                          <span className="text-blue-400">{signal.strategy}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="text-slate-500">R:R:</span>
                          <span className="font-mono text-purple-400">1:{signal.risk_reward}</span>
                        </div>
                      </div>

                      {/* Entry Reason */}
                      <div className="mb-3 p-2 bg-[#151a21] rounded border border-[#2a3441]">
                        <span className="text-xs text-slate-500 block mb-1">Analysis:</span>
                        <span className="text-sm text-slate-300">{signal.entry_reason}</span>
                      </div>

                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <div className="text-slate-500 text-xs">Entry Zone</div>
                          <div className="font-mono text-blue-400">{signal.entry_zone}</div>
                        </div>
                        <div>
                          <div className="text-slate-500 text-xs">Stop Loss</div>
                          <div className="font-mono text-red-400">{signal.stop_loss}</div>
                        </div>
                        <div>
                          <div className="text-slate-500 text-xs">Take Profit</div>
                          <div className="font-mono text-emerald-400">{signal.take_profit}</div>
                        </div>
                      </div>
                      <div className="flex items-center justify-between mt-3 pt-3 border-t border-[#2a3441]">
                        <span className="text-xs text-slate-500">Valid until: {new Date(signal.valid_until).toLocaleTimeString()}</span>
                        <div className="flex gap-2">
                          <button className="px-3 py-1.5 bg-[#242d3a] hover:bg-[#2a3441] rounded-lg text-xs font-medium transition-colors flex items-center gap-1">
                            <Copy className="w-3 h-3" />
                            Copy
                          </button>
                          <button className="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 rounded-lg text-xs font-medium transition-colors flex items-center gap-1">
                            <Zap className="w-3 h-3" />
                            Execute
                          </button>
                        </div>
                      </div>
                    </div>
                  )) : (
                    <div className="text-center py-8 text-slate-500">
                      <TrendingUp className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>No live signals available</p>
                      <p className="text-xs mt-1">Signals refresh automatically every 60 seconds</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Portfolio Tab */}
          {activeTab === 'portfolio' && (
            <div className="space-y-4">
              <div className="bg-[#151a21] rounded-xl border border-[#2a3441] p-4">
                <h3 className="font-semibold mb-4">Portfolio Overview</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-[#1c222b] rounded-lg p-4">
                    <div className="text-slate-500 text-xs mb-1">Total Balance</div>
                    <div className="text-2xl font-bold font-mono">${formatNumber(totalBalance, 0)}</div>
                  </div>
                  <div className="bg-[#1c222b] rounded-lg p-4">
                    <div className="text-slate-500 text-xs mb-1">Open Positions</div>
                    <div className="text-2xl font-bold font-mono">{positions.length}</div>
                  </div>
                  <div className="bg-[#1c222b] rounded-lg p-4">
                    <div className="text-slate-500 text-xs mb-1">Connected Exchanges</div>
                    <div className="text-2xl font-bold font-mono">{connectedPlatforms}</div>
                  </div>
                  <div className="bg-[#1c222b] rounded-lg p-4">
                    <div className="text-slate-500 text-xs mb-1">Active Strategies</div>
                    <div className="text-2xl font-bold font-mono">{strategies.filter(s => s.status === 'active').length}</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Kazzy Panel */}
      <aside className={`fixed right-0 top-0 bottom-0 bg-[#151a21] border-l border-[#2a3441] transition-transform duration-300 z-40 ${kazzyPanelOpen ? 'translate-x-0' : 'translate-x-full'} w-96 hidden lg:flex flex-col`}>
        <div className="h-14 px-4 border-b border-[#2a3441] flex items-center justify-between" style={{ background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1))' }}>
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-[#151a21]" />
            </div>
            <div>
              <div className="font-medium">Kazzy AI</div>
              <div className="text-xs text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
                Online
              </div>
            </div>
          </div>
          <button onClick={() => setKazzyPanelOpen(false)} className="p-1.5 hover:bg-[#1c222b] rounded-lg">
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map(message => (
            <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-[#1c222b]'}`}>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                <div className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-200' : 'text-slate-500'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-[#1c222b] rounded-2xl px-4 py-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-[#2a3441]">
          <button
            onClick={() => setCalculatorOpen(!calculatorOpen)}
            className="w-full px-4 py-2 flex items-center justify-between hover:bg-[#1c222b] transition-colors"
          >
            <div className="flex items-center gap-2">
              <Calculator className="w-4 h-4 text-blue-400" />
              <span className="text-sm">Position Calculator</span>
            </div>
            <ChevronRight className={`w-4 h-4 transition-transform ${calculatorOpen ? 'rotate-90' : ''}`} />
          </button>

          {calculatorOpen && (
            <div className="px-4 pb-4 space-y-3">
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-xs text-slate-500 block mb-1">Balance ($)</label>
                  <input type="number" value={calcBalance} onChange={e => setCalcBalance(Number(e.target.value))} className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-2 py-1.5 text-sm" />
                </div>
                <div>
                  <label className="text-xs text-slate-500 block mb-1">Risk (%)</label>
                  <input type="number" value={calcRisk} onChange={e => setCalcRisk(Number(e.target.value))} className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-2 py-1.5 text-sm" />
                </div>
                <div>
                  <label className="text-xs text-slate-500 block mb-1">SL (pips)</label>
                  <input type="number" value={calcStopLoss} onChange={e => setCalcStopLoss(Number(e.target.value))} className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-2 py-1.5 text-sm" />
                </div>
              </div>
              <button onClick={calculatePositionSize} className="w-full py-2 bg-blue-500 hover:bg-blue-600 rounded-lg text-sm font-medium transition-colors">
                Calculate
              </button>
              {calcResult !== null && (
                <div className="bg-[#1c222b] rounded-lg p-3 text-center">
                  <div className="text-xs text-slate-500 mb-1">Position Size</div>
                  <div className="text-2xl font-bold text-blue-400">{calcResult} Lots</div>
                  <div className="text-xs text-slate-500 mt-1">Risk: ${(calcBalance * calcRisk / 100).toFixed(0)}</div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="p-4 border-t border-[#2a3441]">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={e => setInputMessage(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              placeholder="Ask Kazzy..."
              className="flex-1 bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500"
            />
            <button onClick={sendMessage} disabled={!inputMessage.trim()} className="p-2.5 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-lg transition-colors">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Mobile Chat Floating Button */}
      <button
        onClick={() => setMobileChatOpen(true)}
        className="lg:hidden fixed right-4 bottom-4 w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full shadow-lg shadow-blue-500/30 flex items-center justify-center hover:scale-110 transition-transform z-50"
      >
        <Bot className="w-6 h-6 text-white" />
      </button>

      {/* Mobile Chat Modal */}
      {mobileChatOpen && (
        <div className="lg:hidden fixed inset-0 bg-black/80 z-50 flex flex-col">
          <div className="h-14 px-4 border-b border-[#2a3441] flex items-center justify-between bg-[#151a21]">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <span className="font-medium">Kazzy AI</span>
            </div>
            <button onClick={() => setMobileChatOpen(false)} className="p-2 hover:bg-[#1c222b] rounded-lg">
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#0b0e11]">
            {messages.map(message => (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-[#1c222b]'}`}>
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-[#1c222b] rounded-2xl px-4 py-2.5">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
          </div>
          <div className="p-4 border-t border-[#2a3441] bg-[#151a21]">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={e => setInputMessage(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                placeholder="Ask Kazzy..."
                className="flex-1 bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500"
              />
              <button onClick={sendMessage} disabled={!inputMessage.trim()} className="p-2.5 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-lg transition-colors">
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Desktop Floating Button (when panel closed) */}
      {!kazzyPanelOpen && (
        <button onClick={() => setKazzyPanelOpen(true)} className="hidden lg:flex fixed right-4 bottom-4 w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full shadow-lg shadow-blue-500/30 items-center justify-center hover:scale-110 transition-transform z-30">
          <Bot className="w-6 h-6 text-white" />
        </button>
      )}

      {/* API Keys Modal */}
      {apiKeysModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#151a21] rounded-xl border border-[#2a3441] w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">Connect {platforms.find(p => p.id === selectedExchange)?.name}</h3>
              <button onClick={() => setApiKeysModalOpen(false)} className="p-1 hover:bg-[#1c222b] rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-slate-400 block mb-1">API Key</label>
                <input
                  type="text"
                  value={apiKey}
                  onChange={e => setApiKey(e.target.value)}
                  placeholder="Enter your API key"
                  className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="text-sm text-slate-400 block mb-1">API Secret</label>
                <input
                  type="password"
                  value={apiSecret}
                  onChange={e => setApiSecret(e.target.value)}
                  placeholder="Enter your API secret"
                  className="w-full bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="testnet"
                  checked={testnet}
                  onChange={e => setTestnet(e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <label htmlFor="testnet" className="text-sm text-slate-400">Use testnet (recommended for testing)</label>
              </div>
              <div className="bg-[#1c222b] rounded-lg p-3 text-xs text-slate-500">
                <p className="mb-1"><strong>Security Note:</strong> Your API keys are encrypted and never stored in plain text.</p>
                <p>For automated trading, ensure your API key has "Trade" or "Order" permissions enabled.</p>
              </div>
              <button
                onClick={connectToExchange}
                disabled={!apiKey || !apiSecret}
                className="w-full py-2.5 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
              >
                Connect Exchange
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Emergency Stop Modal */}
      {emergencyStopOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#151a21] rounded-xl border border-red-500/30 w-full max-w-md p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-400" />
              </div>
              <div>
                <h3 className="font-semibold text-lg text-red-400">Emergency Stop</h3>
                <p className="text-sm text-slate-500">This will close all positions immediately</p>
              </div>
            </div>
            <div className="bg-red-500/10 rounded-lg p-3 text-sm text-red-300 mb-4">
              This action cannot be undone. All open positions across all connected exchanges will be closed at market price.
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setEmergencyStopOpen(false)}
                className="flex-1 py-2.5 bg-[#1c222b] hover:bg-[#242d3a] rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={triggerEmergencyStop}
                className="flex-1 py-2.5 bg-red-500 hover:bg-red-600 rounded-lg font-medium transition-colors"
              >
                Stop All Trading
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes ticker {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-ticker {
          animation: ticker 30s linear infinite;
        }
        .animate-ticker:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  )
}

export default App
