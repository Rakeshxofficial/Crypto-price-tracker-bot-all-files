# AI Crypto Assistant Bot

A sophisticated Telegram bot for cryptocurrency analysis, trading, and portfolio management with advanced AI-powered features.

## Features

### Core Functionality
- **AI Market Analysis** - GPT-4 powered buy/sell recommendations
- **Live Price Notifications** - Real-time cryptocurrency price updates
- **Cross-Chain Swaps** - Multi-blockchain token swapping via Rango Exchange
- **Multi-Wallet System** - BIP39 mnemonic generation with multi-chain support
- **Price Alerts** - Customizable price monitoring and notifications
- **Portfolio Tracking** - Comprehensive wallet and asset management

### Advanced Features
- **Technical Charts** - Price history with indicators and volume overlays
- **Token Risk Analysis** - AI-powered scam detection for multiple networks
- **Currency Conversion** - Global fiat currency support with live exchange rates
- **Educational Quizzes** - Interactive crypto learning system
- **Recommendation Engine** - Personalized investment suggestions

### Supported Networks
- Ethereum (ETH)
- Binance Smart Chain (BSC)
- Polygon (MATIC)
- Solana (SOL)
- Tron (TRX)
- Bitcoin (BTC)
- And 80+ other blockchains via Rango Exchange

## Installation

### Requirements
- Python 3.11+
- PostgreSQL database
- Required API keys (see Environment Variables)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/Rakeshxofficial/Marketbot.git
cd Marketbot
```

2. Install dependencies:
```bash
pip install -r pyproject.toml
```

3. Set environment variables (see below)

4. Run the bot:
```bash
python main.py
```

## Environment Variables

Required environment variables:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=your_postgresql_url
OPENAI_API_KEY=your_openai_key
COINGECKO_API_KEY=your_coingecko_key
RANGO_API_KEY=your_rango_exchange_key
COVALENT_API_KEY=your_covalent_key
TRON_API_KEY=your_tron_key
```

## Deployment

### Production Deployment
Use the production startup script for deployment:
```bash
python start_production.py
```

### Docker Deployment
```bash
docker-compose up -d
```

### Platform-Specific
- **Replit**: Use the provided workflow configuration
- **Heroku**: Deploy with the included Dockerfile
- **Railway**: Compatible with the deployment script

## Bot Commands

### Basic Commands
- `/start` - Initialize bot and show main menu
- `/price <coin>` - Get current cryptocurrency price
- `/chart <coin>` - Generate price chart with technical indicators
- `/shouldibuy <coin>` - AI-powered investment analysis

### Wallet Management
- `/createwallet` - Generate new multi-chain wallet
- `/wallet` - View wallet balances and addresses
- `/send` - Send cryptocurrency transactions

### Advanced Features
- `/swap <from> <to> <amount>` - Cross-chain token swapping
- `/alert <coin> <price>` - Set price alerts
- `/scan <contract>` - Analyze token for risks
- `/portfolio` - View portfolio performance
- `/quiz` - Start crypto education quiz

### Live Notifications
- `/startlive <coin>` - Enable live price updates
- `/stoplive <coin>` - Disable live price updates

## Architecture

### Core Services
- **AI Service** - OpenAI GPT-4 integration for market analysis
- **Price Service** - CoinGecko API for real-time price data
- **Chart Service** - Technical analysis and visualization
- **Wallet Service** - Multi-chain wallet management
- **Alert Service** - Price monitoring and notifications
- **Swap Service** - Rango Exchange integration

### Database Schema
- User management and preferences
- Wallet addresses and keys (encrypted)
- Price alerts and notifications
- AI analysis caching
- Portfolio tracking

## Security Features
- Encrypted wallet storage using Fernet encryption
- Secure mnemonic phrase generation
- Environment variable protection
- Rate limiting and error handling

## API Integrations
- **Telegram Bot API** - Core messaging functionality
- **OpenAI API** - AI-powered market analysis
- **CoinGecko API** - Cryptocurrency price data
- **Rango Exchange API** - Cross-chain swapping
- **Covalent API** - Blockchain data analysis
- **Tron API** - Tron network interactions

## Contributing
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Submit pull request

## License
MIT License

## Support
For support and questions, contact the development team or create an issue in the repository.

## Disclaimer
This bot is for educational and informational purposes only. Always conduct your own research before making investment decisions. Cryptocurrency trading carries significant risk.