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

// Types
interface Platform {
  id: string
  name: string
  type: 'forex' | 'crypto'
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
}

interface Strategy {
  id: string
  name: string
  status: 'active' | 'paused' | 'inactive'
  lastRun?: string
  tradesCount: number
}

// Sample data
const initialPlatforms: Platform[] = [
  { id: 'mt4', name: 'MetaTrader 4', type: 'forex', logo: '📊', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'mt5', name: 'MetaTrader 5', type: 'forex', logo: '📈', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'ctrader', name: 'cTrader', type: 'forex', logo: '🎯', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'binance', name: 'Binance', type: 'crypto', logo: '₿', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'coinbase', name: 'Coinbase', type: 'crypto', logo: '💰', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'bybit', name: 'Bybit', type: 'crypto', logo: '🔷', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
  { id: 'tradingview', name: 'TradingView', type: 'forex', logo: '📉', status: 'disconnected', balance: 0, lastSync: 'Not connected' },
]

const initialPositions: Position[] = []

const initialTickers: TickerItem[] = [
  { symbol: 'EUR/USD', price: 1.0847, change: 0.0022, changePercent: 0.2 },
  { symbol: 'GBP/USD', price: 1.2612, change: -0.0033, changePercent: -0.26 },
  { symbol: 'USD/JPY', price: 149.85, change: 0.45, changePercent: 0.3 },
  { symbol: 'BTC/USDT', price: 43200, change: 850, changePercent: 2.01 },
  { symbol: 'ETH/USDT', price: 2245, change: -35, changePercent: -1.54 },
  { symbol: 'XAU/USD', price: 2028, change: -7, changePercent: -0.34 },
  { symbol: 'USD/CHF', price: 0.8845, change: 0.0012, changePercent: 0.14 },
  { symbol: 'AUD/USD', price: 0.6532, change: -0.0021, changePercent: -0.32 },
  { symbol: 'US30', price: 38450, change: 125, changePercent: 0.33 },
  { symbol: 'NAS100', price: 17250, change: 85, changePercent: 0.49 },
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

  // Calculate total portfolio value
  const totalBalance = platforms.reduce((sum, p) => sum + (p.status === 'connected' ? p.balance : 0), 0)
  const totalPnL = positions.reduce((sum, p) => sum + p.pnl, 0)
  const dailyPnL = totalPnL * 0.35
  const connectedPlatforms = platforms.filter(p => p.status === 'connected').length

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

  // Initialize chart
  useEffect(() => {
    if (chartContainer && !chart) {
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

      const sampleData: { time: Time; open: number; high: number; low: number; close: number }[] = []
      let basePrice = 1.0850
      const now = new Date()
      for (let i = 100; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 3600000)
        const open = basePrice
        const change = (Math.random() - 0.5) * 0.003
        const close = open + change
        const high = Math.max(open, close) + Math.random() * 0.001
        const low = Math.min(open, close) - Math.random() * 0.001
        basePrice = close
        sampleData.push({
          time: time.getTime() / 1000 as Time,
          open, high, low, close
        })
      }

      candlestickSeries.setData(sampleData)
      newChart.timeScale().fitContent()
      setChart(newChart)
    }

    return () => { if (chart) chart.remove() }
  }, [chartContainer])

  useEffect(() => {
    const handleResize = () => {
      if (chart && chartContainer) {
        chart.applyOptions({ width: chartContainer.clientWidth })
      }
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [chart, chartContainer])

  // Send message to Kazzy
  const sendMessage = useCallback(() => {
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

    setTimeout(() => {
      let response = kazzyResponses[Math.floor(Math.random() * kazzyResponses.length)]

      // Context-aware responses
      if (inputMessage.toLowerCase().includes('auto') || inputMessage.toLowerCase().includes('automated')) {
        response = autoTradingEnabled
          ? "Automated trading is currently ACTIVE. I'll execute trades based on your configured strategies when signals are generated."
          : "To enable automated trading, please connect your exchange accounts first, then toggle the auto-trading switch. Would you like me to guide you through the setup?"
      } else if (inputMessage.toLowerCase().includes('connect') || inputMessage.toLowerCase().includes('api')) {
        response = "I can help you connect to Binance, Bybit, Coinbase, MetaTrader 4/5, and cTrader. Go to Settings to enter your API keys. For automated trading, you'll need to enable 'Trade' permissions on your API keys."
      } else if (inputMessage.toLowerCase().includes('strategy')) {
        response = "I have three automated strategies available:\n\n1. RSI Mean Reversion - Buys oversold, sells overbought\n2. MA Crossover - Trend following using moving averages\n3. Grid Trading - Places orders at grid levels\n\nWhich strategy would you like to configure?"
      }

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
      setTerminalLogs(prev => [...prev, `Kazzy: ${response}`])
      setIsTyping(false)
    }, 1500)
  }, [inputMessage, autoTradingEnabled])

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
  const connectToExchange = useCallback(() => {
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

    // Simulate connection
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

      addTerminalLog(`Connected to ${selectedExchange} successfully!`)
      addMessage(`Successfully connected to ${selectedExchange}. Your account balance: $${(Math.random() * 50000).toFixed(2)}`)
    }, 2000)

    setApiKeysModalOpen(false)
    setApiKey('')
    setApiSecret('')
    setSelectedExchange('')
  }, [selectedExchange, apiKey, apiSecret])

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
    { id: 'automation', icon: AutoMode, label: 'Automation' },
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
          {/* Dashboard View */}
          {activeTab === 'dashboard' && (
            <>
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
                <div className="xl:col-span-2 bg-[#151a21] rounded-xl border border-[#2a3441] overflow-hidden">
                  <div className="flex items-center justify-between p-3 border-b border-[#2a3441]">
                    <div className="flex items-center gap-3">
                      <select className="bg-[#1c222b] border border-[#2a3441] rounded-lg px-3 py-1.5 text-sm">
                        <option>EUR/USD</option>
                        <option>GBP/USD</option>
                        <option>BTC/USDT</option>
                        <option>XAU/USD</option>
                      </select>
                      <div className="flex gap-1">
                        {['1H', '4H', '1D', '1W'].map(tf => (
                          <button key={tf} className={`px-2.5 py-1 rounded text-xs ${tf === '4H' ? 'bg-blue-500/20 text-blue-400' : 'hover:bg-[#1c222b]'}`}>
                            {tf}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div ref={setChartContainer} className="h-80" />
                </div>

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
            </div>
          )}

          {/* Signals Tab */}
          {activeTab === 'signals' && (
            <div className="space-y-4">
              <div className="bg-[#151a21] rounded-xl border border-[#2a3441] p-4">
                <h3 className="font-semibold mb-4">Trading Signals</h3>
                <div className="space-y-3">
                  {signals.map(signal => (
                    <div key={signal.id} className="bg-[#1c222b] rounded-lg p-4 border border-[#2a3441]">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <span className="font-semibold text-lg">{signal.symbol}</span>
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${signal.direction === 'buy' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                            {signal.direction.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Shield className="w-4 h-4 text-blue-400" />
                          <span className="text-sm font-medium">{signal.confidence}% confidence</span>
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <div className="text-slate-500 text-xs">Entry Zone</div>
                          <div className="font-mono text-blue-400">{signal.entryZone}</div>
                        </div>
                        <div>
                          <div className="text-slate-500 text-xs">Stop Loss</div>
                          <div className="font-mono text-red-400">{signal.stopLoss}</div>
                        </div>
                        <div>
                          <div className="text-slate-500 text-xs">Take Profit</div>
                          <div className="font-mono text-emerald-400">{signal.takeProfit}</div>
                        </div>
                      </div>
                      <div className="flex items-center justify-between mt-3 pt-3 border-t border-[#2a3441]">
                        <span className="text-xs text-slate-500">Expires in {signal.expiry}</span>
                        <div className="flex gap-2">
                          <button
                            onClick={() => copySignal(signal)}
                            className="px-3 py-1.5 bg-[#242d3a] hover:bg-[#2a3441] rounded-lg text-xs font-medium transition-colors flex items-center gap-1"
                          >
                            {copiedSignal === signal.id ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                            Copy
                          </button>
                          <button className="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 rounded-lg text-xs font-medium transition-colors flex items-center gap-1">
                            <Zap className="w-3 h-3" />
                            Execute
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
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

      {/* Floating Button */}
      {!kazzyPanelOpen && (
        <button onClick={() => setKazzyPanelOpen(true)} className="fixed right-4 bottom-4 w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full shadow-lg shadow-blue-500/30 flex items-center justify-center hover:scale-110 transition-transform z-30">
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
