"""
Kazzy Agent Poe AI Integration Module
Enhanced AI capabilities using Poe API - supports GPT, Claude, Llama, and more
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger("KazzyPoe")

# Available models on Poe
POE_MODELS = {
    "claude-opus": {
        "id": "Claude-Opus-4.5",
        "name": "Claude 4 Opus",
        "description": "Most powerful model for deep analysis",
        "type": "analysis"
    },
    "claude-sonnet": {
        "id": "Claude-Sonnet-4.5",
        "name": "Claude 4 Sonnet",
        "description": "Balanced power and speed",
        "type": "general"
    },
    "gpt-4o": {
        "id": "GPT-4o",
        "name": "GPT-4o",
        "description": "OpenAI's latest flagship",
        "type": "general"
    },
    "gpt-4-turbo": {
        "id": "GPT-4-Turbo",
        "name": "GPT-4 Turbo",
        "description": "Fast GPT-4 variant",
        "type": "general"
    },
    "llama-3": {
        "id": "Llama-3.1-405B",
        "name": "Llama 3.1 405B",
        "description": "Meta's most powerful open model",
        "type": "fast"
    },
    "grok-4": {
        "id": "Grok-4",
        "name": "Grok 4",
        "description": "xAI's reasoning model",
        "type": "reasoning"
    },
    "gemini-pro": {
        "id": "Gemini-1.5-Pro-0801",
        "name": "Gemini 1.5 Pro",
        "description": "Google's multimodal model",
        "type": "multimodal"
    },
    "mixtral": {
        "id": "Mixtral-8x22B",
        "name": "Mixtral 8x22B",
        "description": "Fast open-source mixture",
        "type": "fast"
    }
}


class PoeIntegrator:
    """Poe AI integration for enhanced AI trading - OpenAI compatible"""

    def __init__(self):
        self.api_key = os.environ.get('POE_API_KEY')
        self.client = None
        self.enabled = False
        self.current_model = "Claude-Sonnet-4.5"

        if self.api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url="https://api.poe.com/v1"
                )
                self.enabled = True
                logger.info("✅ Poe AI Integration Enabled")
                logger.info(f"📡 Using Poe API with {len(POE_MODELS)} models available")
            except ImportError:
                logger.warning("⚠️ OpenAI package not installed. Run: pip install openai")
                self.enabled = False
            except Exception as e:
                logger.error(f"❌ Failed to initialize Poe: {e}")
                self.enabled = False
        else:
            logger.info("ℹ️ Poe API key not found. Using rule-based AI.")
            self.enabled = False

    def set_model(self, model_id: str):
        """Set the active AI model"""
        if model_id in POE_MODELS:
            self.current_model = POE_MODELS[model_id]["id"]
            logger.info(f"🔄 Switched to model: {self.current_model}")
        else:
            self.current_model = model_id

    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        return POE_MODELS

    async def analyze_with_poe(self, market_data: Dict, symbol: str, model_type: str = None) -> Dict[str, Any]:
        """Use Poe AI for advanced market analysis"""
        if not self.enabled or not self.client:
            return {
                'using_ai': False,
                'model': 'rule-based',
                'message': 'Poe AI not available'
            }

        model = self.current_model
        if model_type and model_type in POE_MODELS:
            model = POE_MODELS[model_type]["id"]

        try:
            recent_prices = market_data.get('recent_candles', [])
            indicators = market_data.get('indicators', {})
            current_price = market_data.get('current_price', 0)
            volume = market_data.get('volume', 0)

            prompt = f"""You are an expert forex, crypto, and stock trading analyst for Kazzy AI Agent.

Analyze the following market data for {symbol} and provide trading recommendations:

📊 Current Price: ${current_price}
📈 Volume: {volume}

Recent Price Data:
{json.dumps(recent_prices[-10:] if recent_prices else [], indent=2)}

Technical Indicators:
{json.dumps(indicators, indent=2)}

Provide your analysis in JSON format with:
- trend: "bullish", "bearish", or "sideways"
- confidence: 0-100
- recommendation: "BUY", "SELL", or "HOLD"
- reasoning: brief explanation
- risk_level: "low", "medium", or "high"

Return ONLY valid JSON, no markdown formatting."""

            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert trading analyst. Provide detailed, actionable trading insights in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )

            result = response.choices[0].message.content

            try:
                analysis = json.loads(result)
                return {
                    'using_ai': True,
                    'model': model,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat()
                }
            except:
                return {
                    'using_ai': True,
                    'model': model,
                    'raw_analysis': result,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Poe AI analysis error: {e}")
            return {
                'using_ai': False,
                'error': str(e)
            }

    async def chat_with_kazzy(self, message: str, context: Dict) -> Dict[str, Any]:
        """Chat with Poe AI as Kazzy trading assistant"""
        if not self.enabled or not self.client:
            return {
                'success': False,
                'response': 'Poe AI not configured. Please add your Poe API key in Settings.',
                'model': 'none'
            }

        model = self.current_model

        try:
            portfolio = context.get('portfolio', {})
            positions = context.get('positions', [])
            balance = context.get('balance', 0)
            open_positions = context.get('open_positions', [])
            prices = context.get('prices', {})

            system_prompt = f"""You are Kazzy, an advanced AI-powered trading assistant.

Your capabilities:
- Execute trades across Forex, Crypto, Stocks, Commodities, Indices, Options, Futures, Bonds, and CFDs
- Analyze markets using technical indicators
- Provide trading signals and recommendations
- Execute automated trading strategies

Current User Status:
- Total Balance: ${balance:,.2f}
- Open Positions: {len(open_positions)}
- Positions: {', '.join([p.get('symbol', 'Unknown') for p in open_positions]) if open_positions else 'None'}

Recent Market Prices:
{json.dumps(prices, indent=2) if prices else 'No price data'}

Trading Capabilities:
- FOREX: EUR/USD, GBP/USD, USD/JPY, and 30+ pairs
- CRYPTO: BTC, ETH, SOL, XRP, ADA, DOGE, and 100+ coins
- STOCKS: AAPL, MSFT, GOOGL, TSLA, NVDA, and 10,000+ stocks
- COMMODITIES: Gold (XAU/USD), Silver (XAG/USD), Oil (WTI, BRENT)
- INDICES: US30, US500, NAS100, UK100, GER40
- FUTURES: ES, NQ, YM, CL, GC

When user gives trade commands (buy, sell, close), respond with JSON:
{{"action": "buy|sell|close|analyze|status|stop|pause|resume|help", "symbol": "SYMBOL", "amount": 0.01, "response": "message"}}

Otherwise respond naturally as a helpful trading assistant."""

            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            result = response.choices[0].message.content

            return {
                'success': True,
                'response': result,
                'model': model,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Poe AI chat error: {e}")
            return {
                'success': False,
                'response': f"AI Error: {str(e)}",
                'model': model,
                'error': str(e)
            }

    async def generate_trading_signal(self, symbol: str, market_data: Dict) -> Dict[str, Any]:
        """Generate a trading signal using Poe AI"""
        if not self.enabled or not self.client:
            return None

        model = self.current_model

        try:
            prompt = f"""Generate a trading signal for {symbol}.

Market Data:
{json.dumps(market_data, indent=2)}

Provide a trading signal in JSON format:
{{
    "symbol": "{symbol}",
    "signal": "BUY" or "SELL" or "HOLD",
    "entry_price": suggested entry,
    "stop_loss": stop loss level,
    "take_profit": take profit level,
    "confidence": 0-100,
    "reasoning": "brief explanation"
}}

Return ONLY valid JSON."""

            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a trading signal generator. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )

            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as e:
            logger.error(f"Poe signal generation error: {e}")
            return None


# Global instance
poe_integrator = PoeIntegrator()
