# Quantitative Trading Platform
## Barney Todd
### Nov 2025
# 📈 QuantApp  
A full-stack quantitative research and trading platform integrating data ingestion, strategy development, backtesting, portfolio optimisation, and simulation into a unified analytical workflow. <br>
The system combines statistical modelling, systematic trading concepts, and scalable software engineering to enable professional-grade quantitative research with production-ready architecture. <br>
Designed to build, test and deploy systematic trading strategies efficiently, mimicking a professional quant workflow.

---

<details>
<summary><strong>🚀 Features</strong></summary>

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

</details>

---

<details>
<summary><strong>🧱 Tech Stack</strong></summary>

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

</details>

---

<details>
<summary><strong>🐳 Run the Application with Docker</strong></summary>

No local installation of Python, Node, or SQL Server needed.
**Docker is required**. You can install it from [here](https://www.docker.com/get-started).


### **1. Clone the repository**
```bash
git clone https://github.com/barneytodd/quantApp.git
cd quantApp
```


### **2. Configure the environment**
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```


### **3. Start all services**
```bash
docker compose up
```

- The **frontend** will be available at [http://localhost:3000](http://localhost:3000)  
- The **backend Swagger documentation** can be accessed at [http://localhost:8001](http://localhost:8001/docs)  

> **Tip:** To run the services in the background (detached mode), use:
```bash
docker compose up -d
```

> To stop all running containers:
```bash
docker compose down
```

> **Tip for development:** If you make changes to the code and need to rebuild the containers, use:
```bash
docker compose up --build
```

</details>
