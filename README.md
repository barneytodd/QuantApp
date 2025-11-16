# Quantative Trading Platform
## Barney Todd
### Nov 2025
# 📈 QuantApp  
A full-stack quantitative research and trading platform integrating data ingestion, strategy development, backtesting, portfolio optimisation, and simulation into a unified analytical workflow.  
The system combines statistical modelling, systematic trading concepts, and scalable software engineering to enable end-to-end quantitative research with a production-ready architecture.

---

## 🚀 Features

### **📊 1. Market Data & Analytics**
- Historical market data ingestion (yfinance)  
- Interactive charts (equity curves, rolling metrics, indicators)  
- Performance statistics: Sharpe ratio, drawdown, volatility  

### **🤖 2. Strategy Backtester**
Built-in strategy modules:
- Momentum  
- Bollinger / RSI mean reversion  
- Moving average crossover  
- Breakout  
- Pairs trading (correlation + cointegration screening)

Includes:
- Parameter sweeps  
- Hyperparameter optimisation (Optuna)  
- Trade logs, PnL tables, execution metrics  

### **📈 3. Portfolio Optimiser**
6-stage automated pipeline:
1. Universe filtering  
2. Asset screening  
3. Preliminary backtests  
4. Strategy selection  
5. Parameter optimisation  
6. Weight optimisation (HRP & Mean-Variance)

### **💹 4. Trading Simulator**
- Executes strategies over time  
- Tracks trades, PnL, risk, and exposure  
- Shares code paths with the backtester for consistency  

---

## 🧱 Tech Stack

### **Backend**
- FastAPI (Python)  
- Pandas, NumPy, SciPy  
- SQLAlchemy ORM  
- Statsmodels (cointegration tests)  
- Optuna (optimisation)  
- MS SQL Server backend

### **Frontend**
- React  
- TailwindCSS  
- Recharts / Plotly visualisations  
- Server-Sent Events for async updates

### **Deployment**
- Docker & Docker Compose  
- Nginx frontend container  
- Preconfigured backend + database services  

---

# 🐳 Run the Entire Application with Docker

No local installation of Python, Node, or SQL Server needed.

### **1. Clone the repository**
```bash
git clone https://github.com/barneytodd/quantApp.git
cd quantApp


