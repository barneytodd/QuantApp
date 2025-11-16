# 📈 Quantitative Trading Platform
## Barney Todd - Nov 2025

A full-stack quantitative research and trading platform integrating data ingestion, strategy development, backtesting, portfolio optimisation, and simulation into a unified analytical workflow. <br>
The system combines statistical modelling, systematic trading concepts, and scalable software engineering to enable professional-grade quantitative research with production-ready architecture. <br>
Designed to build, test and deploy systematic trading strategies efficiently, mimicking a professional quant workflow.

> A full in-depth analysis of the project, including methodology, implementation details, and results, is available in [ProjectWriteup.pdf](ProjectWriteup.pdf).

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
<summary><strong>📊 Results & Current Limitations</strong></summary>

### **Results**
- **Risk reduction:** All model portfolios achieved substantially lower volatility and maximum drawdowns (~40-50%) compared with the S&P 500 benchmark, with stable performance across training and testing periods.  
- **Performance consistency:** Portfolios showed smoother returns and greater resilience during market stress, notably outperforming the benchmark in the 2022 downturn.  
- **Out-of-sample generalization:** Early test results closely matched training performance for most portfolios, suggesting effective avoidance of overfitting.  
- **Portfolio optimization:** HRP-based weight optimization improved risk-adjusted performance in most portfolios, though concentrated or regime-shifting environments reduced effectiveness for some cases.  
- **Combined portfolio:** Provided balanced risk-adjusted returns, lowering volatility and drawdowns while generally underperforming benchmarks in strong recovery years.

### **Limitations**
- **Backtesting assumptions:** Uses daily data only; intraday dynamics and high-frequency effects are not modeled.  
- **Strategy scope:** Limited to basic long-only strategies and hyperparameters; complex portfolios not yet supported.  
- **Market frictions:** Slippage and liquidity effects are simplified.  
- **Optimization framework:** Currently classical mean-variance; advanced risk models (CVaR, Black-Litterman) not implemented.  
- **Simulator constraints:** Operates in a controlled environment without live broker API integration.
- **Generalisation during regime shifts:** Performance can deteriorate during rapid or extreme market regime changes.

### Planned Improvements
- Integrate regime-awareness into the optimizer using HMM or clustering-based classifiers.  
- Enhance asset selection and expected return estimation for changing market conditions.  
- Expand strategy scope, include advanced risk models, and support live trading integration.

> These results demonstrate that the platform can generate robust, risk-adjusted portfolios and support quantitative research, while highlighting opportunities for further enhancements in realism, strategy complexity, and live execution.

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

