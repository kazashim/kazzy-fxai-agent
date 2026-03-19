using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using DocForge.Core;

namespace DocForge.Templates;

public static class KazzyAgentManual
{
    private static readonly Themes.ColorSet Theme = Themes.Ocean;

    public static void Build(string outputPath)
    {
        using var doc = WordprocessingDocument.Create(outputPath, WordprocessingDocumentType.Document);
        var main = doc.AddMainDocumentPart();
        main.Document = new Document(new Body());

        var body = main.Document.Body!;

        RenderCover(body);
        RenderToc(body);
        RenderIntroduction(body);
        RenderPlatformSection(body);
        RenderSetupSection(body);
        RenderAutoTradingSection(body);
        RenderLiveFeedsSection(body);
        RenderAISection(body);
        RenderSecuritySection(body);
        RenderTroubleshootingSection(body);

        main.Document.Save();
    }

    private static void RenderCover(Body body)
    {
        body.Append(new Paragraph(new ParagraphProperties(Primitives.Gaps(200, 0))));

        body.Append(new Paragraph(
            new ParagraphProperties(new Justification { Val = JustificationValues.Center }, Primitives.Gaps(0, 20)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 36, Theme.Heading, true), new Text("Kazzy Agent"))
        ));

        body.Append(new Paragraph(
            new ParagraphProperties(new Justification { Val = JustificationValues.Center }, Primitives.Gaps(0, 10)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 18, Theme.Muted), new Text("Automated Trading System"))
        ));

        body.Append(new Paragraph(new ParagraphProperties(Primitives.Gaps(0, 40))));

        body.Append(new Paragraph(
            new ParagraphProperties(new Justification { Val = JustificationValues.Center }),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 14, Theme.Body), new Text("Complete User Guide"))
        ));

        body.Append(new Paragraph(
            new ParagraphProperties(new Justification { Val = JustificationValues.Center }, Primitives.Gaps(0, 8)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 12, Theme.Muted), new Text("API Integration & Trading Platform Setup"))
        ));

        body.Append(new Paragraph(new ParagraphProperties(Primitives.Gaps(80, 0))));

        body.Append(new Paragraph(
            new ParagraphProperties(new Justification { Val = JustificationValues.Center }),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 11, Theme.Muted), new Text($"Version 1.0 | {DateTime.UtcNow:yyyy-MM-dd}"))
        ));
    }

    private static void RenderToc(Body body)
    {
        AddPageBreak(body);
        body.Append(ChapterTitle("Table of Contents", 22));

        body.Append(new Paragraph(
            new ParagraphProperties(Primitives.Gaps(6, 8)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 12, Theme.Body, true), new Text("1. Introduction to Kazzy Agent"))
        ));

        body.Append(new Paragraph(
            new ParagraphProperties(Primitives.Gaps(6, 8)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 12, Theme.Body, true), new Text("2. Supported Trading Platforms"))
        ));

        body.Append(new Paragraph(
            new ParagraphProperties(Primitives.Gaps(6, 8)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 12, Theme.Body, true), new Text("3. Platform API Setup"))
        ));

        body.Append(new Paragraph(
            new ParagraphProperties(Primitives.Gaps(6, 8)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 12, Theme.Body, true), new Text("4. Auto-Trading Configuration"))
        ));

        body.Append(new Paragraph(
            new ParagraphProperties(Primitives.Gaps(6, 8)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 12, Theme.Body, true), new Text("5. Live Trading Feeds"))
        ));

        body.Append(new Paragraph(
            new ParagraphProperties(Primitives.Gaps(6, 8)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 12, Theme.Body, true), new Text("6. AI Integration"))
        ));

        body.Append(new Paragraph(
            new ParagraphProperties(Primitives.Gaps(6, 8)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 12, Theme.Body, true), new Text("7. Security Best Practices"))
        ));

        body.Append(new Paragraph(
            new ParagraphProperties(Primitives.Gaps(6, 8)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 12, Theme.Body, true), new Text("8. Troubleshooting"))
        ));
    }

    private static void RenderIntroduction(Body body)
    {
        AddPageBreak(body);
        body.Append(ChapterTitle("1. Introduction to Kazzy Agent", 20));

        AddParagraph(body, "Kazzy Agent is an advanced AI-powered automated trading system designed to connect to multiple trading platforms and execute trades autonomously. This comprehensive guide will help you set up and configure your trading accounts.");
        AddParagraph(body, "");
        AddParagraph(body, "Key Features:");
        AddBullet(body, "Universal exchange connectivity (30+ platforms)");
        AddBullet(body, "Real-time market data and live trading feeds");
        AddBullet(body, "AI-powered signal generation and analysis");
        AddBullet(body, "Automated trading with risk management");
        AddBullet(body, "Poe AI integration for advanced intelligence");
        AddBullet(body, "Multi-asset support (Forex, Crypto, Stocks, Commodities, Indices, Options, Futures, Bonds, CFDs)");
    }

    private static void RenderPlatformSection(Body body)
    {
        AddPageBreak(body);
        body.Append(ChapterTitle("2. Supported Trading Platforms", 20));

        AddParagraph(body, "Kazzy Agent supports the following trading platforms:");

        AddParagraph(body, "");
        AddParagraph(body, "FOREX PLATFORMS");
        AddBullet(body, "MetaTrader 4 (MT4) - Popular forex trading platform");
        AddBullet(body, "MetaTrader 5 (MT5) - Advanced forex and CFD trading");
        AddBullet(body, "cTrader - Professional forex trading platform");
        AddBullet(body, "FXCM - Global forex broker");
        AddBullet(body, "IC Markets - ECN forex broker");

        AddParagraph(body, "");
        AddParagraph(body, "CRYPTOCURRENCY EXCHANGES");
        AddBullet(body, "Binance - World's largest crypto exchange");
        AddBullet(body, "Coinbase - US-based regulated exchange");
        AddBullet(body, "Bybit - Derivatives-focused exchange");
        AddBullet(body, "Kraken - Security-first exchange");
        AddBullet(body, "KuCoin - Multi-chain trading");
        AddBullet(body, "OKX - Global crypto exchange");

        AddParagraph(body, "");
        AddParagraph(body, "STOCK TRADING");
        AddBullet(body, "Interactive Brokers (IBKR) - Professional trading");
        AddBullet(body, "Alpaca - Commission-free stock trading API");
        AddBullet(body, "TD Ameritrade - Full-service brokerage");
        AddBullet(body, "Fidelity - Traditional brokerage");
        AddBullet(body, "Charles Schwab - Investment services");

        AddParagraph(body, "");
        AddParagraph(body, "COMMODITIES & INDICES");
        AddBullet(body, "Precious Metals (Gold, Silver, Platinum)");
        AddBullet(body, "Energy (Oil, Natural Gas)");
        AddParagraph(body, "");
        AddParagraph(body, "OPTIONS & FUTURES");
        AddBullet(body, "IBKR Options");
        AddBullet(body, "ThinkOrSwim");
        AddBullet(body, "CME Group");

        AddParagraph(body, "");
        AddParagraph(body, "BONDS & CFDs");
        AddBullet(body, "US Treasury Bonds");
        AddBullet(body, "Corporate Bonds");
        AddBullet(body, "MT5 CFDs");
        AddBullet(body, "IG Markets");
        AddBullet(body, "OANDA");
    }

    private static void RenderSetupSection(Body body)
    {
        AddPageBreak(body);
        body.Append(ChapterTitle("3. Platform API Setup", 20));

        AddParagraph(body, "This section provides step-by-step instructions for obtaining API keys from each supported platform.");
        AddParagraph(body, "");

        AddSubSection(body, "3.1 Binance API Setup");
        AddParagraph(body, "Step 1: Log in to your Binance account at https://www.binance.com");
        AddParagraph(body, "Step 2: Navigate to API Management (Account > API Management)");
        AddParagraph(body, "Step 3: Click 'Create API' and enter a label for your key");
        AddParagraph(body, "Step 4: Complete security verification (2FA)");
        AddParagraph(body, "Step 5: Copy your API Key and Secret Key immediately");
        AddParagraph(body, "Important: Enable 'Enable Trading' permission for automated trading");
        AddParagraph(body, "Note: For enhanced security, set IP restrictions if possible");

        AddParagraph(body, "");
        AddSubSection(body, "3.2 MetaTrader 5 (MT5) API Setup");
        AddParagraph(body, "Option A: Using MetaQuotes Cloud (Recommended)");
        AddParagraph(body, "1. Install MT5 terminal from https://www.metatrader5.com/");
        AddParagraph(body, "2. Create or log into your MT5 account");
        AddParagraph(body, "3. Go to Tools > Options > API");
        AddParagraph(body, "4. Enable API access and note the server details");
        AddParagraph(body, "");
        AddParagraph(body, "Option B: Using Third-Party Solutions");
        AddParagraph(body, "1. Services like MT5API.cloud provide REST API access");
        AddParagraph(body, "2. Register at https://metatraderapi.cloud/");
        AddParagraph(body, "3. Follow their setup guide to get API credentials");

        AddParagraph(body, "");
        AddSubSection(body, "3.3 Coinbase API Setup");
        AddParagraph(body, "Step 1: Log in to Coinbase at https://www.coinbase.com");
        AddParagraph(body, "Step 2: Go to Settings > API Access");
        AddParagraph(body, "Step 3: Click 'New API Key'");
        AddParagraph(body, "Step 4: Select permissions: 'Read' and 'Trade' (avoid 'Transfer' for security)");
        AddParagraph(body, "Step 5: Save your API Key and Secret");

        AddParagraph(body, "");
        AddSubSection(body, "3.4 Bybit API Setup");
        AddParagraph(body, "Step 1: Log in to Bybit at https://www.bybit.com");
        AddParagraph(body, "Step 2: Click your profile icon > API");
        AddParagraph(body, "Step 3: Click 'Create New Key'");
        AddParagraph(body, "Step 4: Enter a name for the API key");
        AddParagraph(body, "Step 5: Select API key permissions (Enable Trading for automated trading)");
        AddParagraph(body, "Step 6: Complete security verification");
        AddParagraph(body, "Step 7: Copy API Key and Secret immediately");

        AddParagraph(body, "");
        AddSubSection(body, "3.5 Interactive Brokers (IBKR) API Setup");
        AddParagraph(body, "Step 1: Log in to IBKR Client Portal");
        AddParagraph(body, "Step 2: Go to Settings > API Settings");
        AddParagraph(body, "Step 3: Click 'Create API Key'");
        AddParagraph(body, "Step 4: Configure permissions and IP restrictions");
        AddParagraph(body, "Step 5: Download and save your credentials");

        AddParagraph(body, "");
        AddSubSection(body, "3.6 Connecting via Frontend");
        AddParagraph(body, "After obtaining your API keys:");
        AddParagraph(body, "1. Open the Kazzy Agent dashboard");
        AddParagraph(body, "2. Navigate to the Settings tab");
        AddParagraph(body, "3. Select your trading platform from the list");
        AddParagraph(body, "4. Enter your API Key and API Secret");
        AddParagraph(body, "5. Enable 'Testnet' for testing before live trading");
        AddParagraph(body, "6. Click 'Connect Exchange'");
    }

    private static void RenderAutoTradingSection(Body body)
    {
        AddPageBreak(body);
        body.Append(ChapterTitle("4. Auto-Trading Configuration", 20));

        AddSubSection(body, "4.1 Enabling Auto-Trading");
        AddParagraph(body, "Kazzy Agent can automatically execute trades based on AI-generated signals:");
        AddParagraph(body, "");
        AddParagraph(body, "1. Connect at least one exchange with API keys");
        AddParagraph(body, "2. Go to the Automation tab in the dashboard");
        AddParagraph(body, "3. Enable 'Master Control' toggle");
        AddParagraph(body, "4. Configure your risk parameters:");
        AddBullet(body, "Max Risk per Trade (%)");
        AddBullet(body, "Max Daily Loss (%)");
        AddBullet(body, "Maximum Open Positions");
        AddParagraph(body, "5. Select trading strategies (RSI, MA Crossover, Grid)");
        AddParagraph(body, "6. Click 'Start Auto-Trading'");

        AddParagraph(body, "");
        AddSubSection(body, "4.2 AI Signal Generation");
        AddParagraph(body, "Kazzy Agent analyzes markets using multiple indicators:");
        AddBullet(body, "RSI (Relative Strength Index)");
        AddBullet(body, "MACD (Moving Average Convergence Divergence)");
        AddBullet(body, "Support and Resistance levels");
        AddBullet(body, "Trend analysis");
        AddBullet(body, "Volume analysis");
        AddParagraph(body, "AI signals are generated with confidence scores to help you make informed decisions.");

        AddParagraph(body, "");
        AddSubSection(body, "4.3 Risk Management");
        AddParagraph(body, "Always configure risk parameters before enabling auto-trading:");
        AddParagraph(body, "");
        AddParagraph(body, "Conservative: 1-2% risk per trade");
        AddParagraph(body, "Moderate: 2-5% risk per trade");
        AddParagraph(body, "Aggressive: 5-10% risk per trade (not recommended)");
    }

    private static void RenderLiveFeedsSection(Body body)
    {
        AddPageBreak(body);
        body.Append(ChapterTitle("5. Live Trading Feeds", 20));

        AddParagraph(body, "Kazzy Agent provides real-time streaming data from all connected exchanges.");
        AddParagraph(body, "");

        AddSubSection(body, "5.1 Available Feed Types");
        AddBullet(body, "Ticker Prices - Real-time bid/ask prices");
        AddBullet(body, "Order Book - Market depth visualization");
        AddBullet(body, "Positions - Live position tracking");
        AddBullet(body, "Balance - Account equity updates");
        AddBullet(body, "System - Trade execution notifications");

        AddParagraph(body, "");
        AddSubSection(body, "5.2 Enabling Live Feeds");
        AddParagraph(body, "1. Navigate to the Dashboard tab");
        AddParagraph(body, "2. Look for the Live Feeds panel");
        AddParagraph(body, "3. Click 'Start Live Feeds'");
        AddParagraph(body, "4. Prices will update in real-time");
        AddParagraph(body, "5. Use 'Stop Live Feeds' to pause streaming");

        AddParagraph(body, "");
        AddSubSection(body, "5.3 API Endpoints for Live Data");
        AddParagraph(body, "For developers integrating with Kazzy Agent:");
        AddParagraph(body, "");
        AddParagraph(body, "POST /api/feeds/start - Start streaming");
        AddParagraph(body, "POST /api/feeds/stop - Stop streaming");
        AddParagraph(body, "GET /api/feeds/prices - Get current prices");
        AddParagraph(body, "GET /api/feeds/status - Get feed status");
    }

    private static void RenderAISection(Body body)
    {
        AddPageBreak(body);
        body.Append(ChapterTitle("6. AI Integration", 20));

        AddSubSection(body, "6.1 Poe AI Integration");
        AddParagraph(body, "Kazzy Agent uses Poe's AI API for advanced market analysis and decision-making.");
        AddParagraph(body, "");
        AddParagraph(body, "Supported Models:");
        AddBullet(body, "Claude 4 Opus - Deep analysis");
        AddBullet(body, "Claude 4 Sonnet - Balanced performance");
        AddBullet(body, "GPT-4o - OpenAI flagship");
        AddBullet(body, "GPT-4 Turbo - Fast GPT-4");
        AddBullet(body, "Llama 3.1 405B - Meta open model");
        AddBullet(body, "Grok 4 - xAI reasoning");
        AddBullet(body, "Gemini 1.5 Pro - Google multimodal");

        AddParagraph(body, "");
        AddSubSection(body, "6.2 Setting Up Poe API");
        AddParagraph(body, "1. Go to https://poe.com and create an account");
        AddParagraph(body, "2. Subscribe to a plan (free tier available)");
        AddParagraph(body, "3. Navigate to Settings > API");
        AddParagraph(body, "4. Generate your API key");
        AddParagraph(body, "5. In Kazzy Agent, go to Settings");
        AddParagraph(body, "6. Enter your Poe API key");
        AddParagraph(body, "7. Select your preferred AI model");

        AddParagraph(body, "");
        AddSubSection(body, "6.3 AI Learning System");
        AddParagraph(body, "Kazzy Agent continuously learns from your trading data:");
        AddBullet(body, "Pattern detection - Identifies recurring market patterns");
        AddBullet(body, "Performance analysis - Tracks win rate and profit factor");
        AddBullet(body, "Strategy optimization - Suggests improvements");
        AddBullet(body, "Risk assessment - Evaluates portfolio risk");
    }

    private static void RenderSecuritySection(Body body)
    {
        AddPageBreak(body);
        body.Append(ChapterTitle("7. Security Best Practices", 20));

        AddParagraph(body, "Protecting your trading accounts and funds is paramount. Follow these security guidelines:");
        AddParagraph(body, "");

        AddSubSection(body, "7.1 API Key Security");
        AddBullet(body, "Never share your API keys with anyone");
        AddBullet(body, "Enable IP restrictions on API keys when possible");
        AddBullet(body, "Use 'Read-Only' permissions if you only need data");
        AddBullet(body, "Enable 'Trade' permissions only when needed");
        AddBullet(body, "Regularly rotate your API keys");
        AddBullet(body, "Never store API keys in plain text files");

        AddParagraph(body, "");
        AddSubSection(body, "7.2 Account Protection");
        AddBullet(body, "Enable Two-Factor Authentication (2FA) on all exchanges");
        AddBullet(body, "Use unique, strong passwords");
        AddBullet(body, "Monitor your accounts regularly");
        AddBullet(body, "Set up withdrawal address whitelisting");
        AddBullet(body, "Review API permissions monthly");

        AddParagraph(body, "");
        AddSubSection(body, "7.3 Trading Risk Controls");
        AddParagraph(body, "Always configure these before auto-trading:");
        AddBullet(body, "Maximum risk per trade (recommended: 1-2%)");
        AddBullet(body, "Daily loss limit (recommended: 5-10%)");
        AddBullet(body, "Maximum concurrent positions");
        AddBullet(body, "Emergency stop button - always accessible");

        AddParagraph(body, "");
        AddSubSection(body, "7.4 Testing");
        AddParagraph(body, "Before trading with real funds:");
        AddBullet(body, "Use testnet/demo accounts when available");
        AddBullet(body, "Start with small position sizes");
        AddParagraph(body, "Verify all settings before enabling auto-trading");
        AddBullet(body, "Monitor initial trades closely");
    }

    private static void RenderTroubleshootingSection(Body body)
    {
        AddPageBreak(body);
        body.Append(ChapterTitle("8. Troubleshooting", 20));

        AddSubSection(body, "8.1 Common Connection Issues");
        AddParagraph(body, "Problem: Cannot connect to exchange");
        AddParagraph(body, "Solutions:");
        AddBullet(body, "Verify API key and secret are correct");
        AddBullet(body, "Check if IP is whitelisted on exchange");
        AddBullet(body, "Ensure API has trading permissions enabled");
        AddBullet(body, "Check if account is verified on the exchange");

        AddParagraph(body, "");
        AddParagraph(body, "Problem: API key invalid error");
        AddParagraph(body, "Solutions:");
        AddBullet(body, "Regenerate API keys on exchange");
        AddBullet(body, "Check for extra spaces in key fields");
        AddBullet(body, "Verify key hasn't expired");

        AddParagraph(body, "");
        AddSubSection(body, "8.2 Trading Issues");
        AddParagraph(body, "Problem: Orders not executing");
        AddParagraph(body, "Solutions:");
        AddBullet(body, "Check account has sufficient balance");
        AddBullet(body, "Verify symbol is available on exchange");
        AddBullet(body, "Check if market is open");
        AddBullet(body, "Review risk limits haven't been reached");

        AddParagraph(body, "");
        AddParagraph(body, "Problem: Position not closing");
        AddParagraph(body, "Solutions:");
        AddBullet(body, "Use Emergency Stop for immediate closure");
        AddBullet(body, "Check internet connection");
        AddBullet(body, "Verify API has 'Trade' permissions");

        AddParagraph(body, "");
        AddSubSection(body, "8.3 Performance Issues");
        AddParagraph(body, "Problem: Slow data updates");
        AddParagraph(body, "Solutions:");
        AddBullet(body, "Check internet connection speed");
        AddBullet(body, "Disable unnecessary browser tabs");
        AddBullet(body, "Use wired connection instead of WiFi");

        AddParagraph(body, "");
        AddParagraph(body, "Problem: AI not generating signals");
        AddParagraph(body, "Solutions:");
        AddBullet(bullet: "Ensure Poe API key is configured");
        AddBullet(body: "Check AI model is selected in settings");
        AddBullet(body: "Verify exchange is connected with data access");

        AddParagraph(body: "");
        AddSubSection(body: "8.4 Support");
        AddParagraph(body: "For additional support:");
        AddBullet(body: "Check Kazzy Agent documentation");
        AddBullet(body: "Review exchange API documentation");
        AddBullet(body: "Contact exchange support for API issues");
    }

    private static void AddPageBreak(Body body)
    {
        body.Append(new Paragraph(new Run(new Break { Type = BreakValues.Page })));
    }

    private static Paragraph ChapterTitle(string text, double size)
    {
        return new Paragraph(
            new ParagraphProperties(Primitives.Gaps(0, 14)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", size, Theme.Heading, true), new Text(text))
        );
    }

    private static void AddSubSection(Body body, string text)
    {
        body.Append(new Paragraph(
            new ParagraphProperties(Primitives.Gaps(0, 10)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 14, Theme.Body, true), new Text(text))
        ));
    }

    private static void AddParagraph(Body body, string text)
    {
        if (string.IsNullOrEmpty(text))
        {
            body.Append(new Paragraph(new ParagraphProperties(Primitives.Gaps(0, 6))));
            return;
        }
        body.Append(new Paragraph(
            new ParagraphProperties(Primitives.Margins(0, 18), Primitives.Gaps(0, 8, 1.15)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 11, Theme.Body), new Text(text))
        ));
    }

    private static void AddBullet(Body body, string text)
    {
        body.Append(new Paragraph(
            new ParagraphProperties(Primitives.Margins(720, 18), Primitives.Gaps(0, 4, 1.15)),
            new Run(Primitives.TextStyle("Arial", "Microsoft YaHei", 11, Theme.Body), new Text("• " + text))
        ));
    }
}
