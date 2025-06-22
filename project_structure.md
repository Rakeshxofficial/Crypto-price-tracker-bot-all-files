# Project Structure

```
Marketbot/
├── main.py                     # Main bot application
├── web_server.py              # Web interface and health endpoint
├── config.py                  # Configuration settings
├── database.py               # Database models and setup
├── 
├── Core Services/
├── ai_service.py             # OpenAI GPT-4 market analysis
├── price_service.py          # CoinGecko price data
├── market_service.py         # Market data aggregation
├── chart_service.py          # Technical chart generation
├── alert_service.py          # Price alerts system
├── live_notification_service.py # Real-time notifications
├── 
├── Wallet & Trading/
├── wallet_service.py         # Basic wallet operations
├── multi_wallet_service.py   # Multi-chain wallet system
├── rango_swap_service.py     # Cross-chain swapping
├── portfolio_service.py      # Portfolio tracking
├── 
├── Analysis & Security/
├── token_scanner.py          # Token contract analysis
├── token_risk_analyzer.py    # AI-powered risk detection
├── recommendation_engine.py  # Investment recommendations
├── 
├── Utilities/
├── coin_mapper.py            # Cryptocurrency symbol mapping
├── currency_converter.py     # Fiat currency conversion
├── user_service.py           # User management
├── quiz_service.py           # Educational quizzes
├── 
├── Deployment/
├── start_production.py       # Production startup script
├── Dockerfile               # Container deployment
├── docker-compose.yml       # Full stack deployment
├── deploy.sh               # Deployment automation
├── deployment_guide.md     # Deployment instructions
├── 
├── Configuration/
├── pyproject.toml          # Python dependencies
├── uv.lock                # Dependency lock file
├── .replit                # Replit configuration
├── wallet_encryption.key  # Encryption key (gitignore)
├── 
└── Documentation/
    ├── README.md              # Main documentation
    ├── project_structure.md   # This file
    └── git_upload_commands.txt # Git commands
```

## Key Components

### Core Bot Logic
- `main.py` - Central bot application with all command handlers
- `web_server.py` - Health monitoring and web interface
- `database.py` - PostgreSQL models for users, wallets, alerts

### Service Architecture
- Modular design with dedicated services for each feature
- Async/await pattern for optimal performance
- Comprehensive error handling and logging

### Security Features
- Encrypted wallet storage
- Secure API key management
- Rate limiting and validation

### Deployment Ready
- Production configurations for multiple platforms
- Docker containerization
- Environment variable management
- Health checks and monitoring