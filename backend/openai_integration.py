"""
Kazzy Agent OpenAI Integration Module
Enhanced AI capabilities using OpenAI GPT models
"""

import os
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("KazzyOpenAI")

# OpenAI Integration
class OpenAIIntegrator:
    """OpenAI GPT integration for enhanced AI trading"""

    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.client = None
        self.enabled = False

        if self.api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
                self.enabled = True
                logger.info("✅ OpenAI Integration Enabled")
            except ImportError:
                logger.warning("⚠️ OpenAI package not installed. Run: pip install openai")
                self.enabled = False
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI: {e}")
                self.enabled = False
        else:
            logger.info("ℹ️ OpenAI API key not found. Using rule-based AI.")
            self.enabled = False

    async def analyze_with_gpt(self, market_data: Dict, symbol: str) -> Dict[str, Any]:
        """
        Use GPT-4 for advanced market analysis
        """
        if not self.enabled or not self.client:
            return {
                'using_ai': False,
                'model': 'rule-based',
                'message': 'OpenAI not available'
            }

        try:
            # Prepare market data summary
            recent_prices = market_data.get('recent_candles', [])
            indicators = market_data.get('indicators', {})

            prompt = f"""Analyze the following market data for {symbol} and provide trading recommendations:

Recent Price Data:
{json.dumps(recent_prices[-10:], indent=2)}

Technical Indicators:
{json.dumps(indicators, indent=2)}

Provide your analysis in JSON format with:
- trend: "bullish", "bearish", or "sideways"
- confidence: 0-100
- recommendation: "BUY", "SELL", or "HOLD"
- reasoning: brief explanation
- risk_level: "low", "medium", or "high"
"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert forex and crypto trading analyst. Provide detailed, actionable trading insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            result = response.choices[0].message.content

            try:
                analysis = json.loads(result)
                return {
                    'using_ai': True,
                    'model': 'gpt-4',
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat()
                }
            except:
                return {
                    'using_ai': True,
                    'model': 'gpt-4',
                    'raw_analysis': result,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            return {
                'using_ai': False,
                'error': str(e)
            }

    async def process_nlp_command(self, command: str, context: Dict) -> Dict[str, Any]:
        """
        Use GPT to understand and process natural language commands
        """
        if not self.enabled or not self.client:
            return None

        try:
            portfolio = context.get('portfolio', {})
            open_positions = context.get('positions', [])
            balance = context.get('balance', 0)

            prompt = f"""A user has given the following command to their trading bot:

Command: "{command}"

Current Portfolio:
- Total Balance: ${balance}
- Open Positions: {len(open_positions)}
- Positions: {json.dumps([p.get('symbol') for p in open_positions])}

Available actions:
- buy [symbol]: Open long position
- sell [symbol]: Close position or open short
- close [symbol]: Close specific position
- analyze [symbol]: Run market analysis
- status: Show portfolio status
- stop: Emergency stop all trading
- pause: Pause automated trading
- resume: Resume automated trading

Determine what action the user wants and provide the response in JSON format:
{{
    "action": "buy|sell|close|analyze|status|stop|pause|resume|unknown",
    "symbol": "symbol name or null",
    "parameters": {{}},
    "response": "Natural language response to show user"
}}
"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful trading bot assistant. Parse user commands and return structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )

            result = response.choices[0].message.content

            try:
                parsed = json.loads(result)
                return parsed
            except:
                return {'action': 'unknown', 'response': result}

        except Exception as e:
            logger.error(f"OpenAI NLP error: {e}")
            return None

    async def generate_market_commentary(self, symbols: list, market_data: Dict) -> str:
        """
        Generate human-readable market commentary
        """
        if not self.enabled or not self.client:
            return None

        try:
            summary = []
            for symbol in symbols:
                data = market_data.get(symbol, {})
                summary.append(f"{symbol}: {data.get('trend', 'unknown')} trend")

            prompt = f"""Generate a brief market commentary for today based on:

Market Summary:
{chr(10).join(summary)}

Write a 2-3 sentence market commentary suitable for traders. Include relevant technical levels if possible.
"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert market analyst. Write concise, informative market commentary."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI commentary error: {e}")
            return None


# Global instance
openai_integrator = OpenAIIntegrator()
