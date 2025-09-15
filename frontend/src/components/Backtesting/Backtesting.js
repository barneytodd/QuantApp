import { useEffect, useState, useMemo } from "react";
import Select from "react-select";
import Chart from "../Chart/Chart";
import { backtestSMA } from "../../utils/backtest";

function Backtesting() {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [shortPeriod, setShortPeriod] = useState(20);
  const [longPeriod, setLongPeriod] = useState(50);
  const [backtestResult, setBacktestResult] = useState(null);
  const [strategyType, setStrategyType] = useState(null);

  const strategyTypeOptions = useMemo(() => [
    { value: 'Moving average crossover', label: 'Moving Average Crossover' }
  ], []); 
  
  // get available ticker symbols from backend
  useEffect(() => {
    fetch("http://localhost:8000/api/symbols")
      .then(res => res.json())
      .then(data => {
        setSymbols(data.map(s => ({ value: s, label: s })));
        setSelectedSymbol({ value: data[0], label: data[0] }); // default first symbol
      });
    
    
    setStrategyType(strategyTypeOptions[0]);
  }, [strategyTypeOptions]);

  const runBacktest = async () => {
    if (!selectedSymbol) return;
    const res = await fetch(`http://localhost:8000/api/ohlcv/${selectedSymbol?.value}?limit=500`);
    const data = await res.json();
    const result = backtestSMA(data, shortPeriod, longPeriod, 10000);
    setBacktestResult(result);
  };

  const optimiseParameters = async () => {
    return;
  }

  
  return (
    <div className="space-y-4">
      
      {/* Strategy type selector */}
      <div className="w-60">
        <h3 className="text-xl font-bold mb-2">Choose a trading strategy:</h3>
        <Select
          options={strategyTypeOptions}
          value={strategyType}
          onChange={setStrategyType}
          isSearchable
          placeholder="Select a type"
          menuPortalTarget={document.body}
          styles={{
            menuPortal: (base) => ({ ...base, zIndex: 9999 })
          }}
        />
      </div>

      {/* Symbol selector */}
      <div className="w-60">
        <h3 className="text-xl font-bold mb-2">Backtest on:</h3>
        <Select
          options={symbols}
          value={selectedSymbol}
          onChange={setSelectedSymbol}
          isSearchable
          placeholder="Select a ticker symbol"
          menuPortalTarget={document.body}  
          styles={{
            menuPortal: (base) => ({ ...base, zIndex: 9999 }) 
          }}
        />
      </div>

      {/* Controls */}
      <h3 className="text-xl font-bold mb-2">Set Parameters:</h3>
      <div className="flex gap-4 items-center">
        <span>Short SMA Period:</span>
        <input
          type="number"
          value={shortPeriod}
          onChange={(e) => setShortPeriod(Number(e.target.value))}
          className="border p-1 rounded"
        />
          
        <span>Long SMA Period:</span>
        <input
          type="number"
          value={longPeriod}
          onChange={(e) => setLongPeriod(Number(e.target.value))}
          className="border p-1 rounded"
        />
        
        <button
          onClick={optimiseParameters}
          className="bg-blue-500 text-white px-4 py-1 rounded"
        >
          OptimiseParameters
        </button>
        
      </div>

      <div className="w-60">
        <h3 className="text-xl font-bold mb-2">Run Test:</h3>
          <button
            onClick={runBacktest}
            className="bg-blue-500 text-white px-4 py-1 rounded"
          >
            Run Backtest
          </button>
      </div>

      {/* Results */}
      {backtestResult && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white p-4 shadow rounded">
            <p className="text-sm text-gray-500">Final Capital</p>
            <p className="text-lg font-bold">${backtestResult.finalCapital.toFixed(2)}</p>
          </div>
          <div className="bg-white p-4 shadow rounded">
            <p className="text-sm text-gray-500">Return %</p>
            <p className="text-lg font-bold">{backtestResult.returnPct.toFixed(2)}%</p>
          </div>
        </div>
      )}

      {/* Equity Curve */}
      {backtestResult && (
        <div className="bg-white p-4 shadow rounded">
          <h3 className="font-bold mb-2">Equity Curve</h3>
          <Chart data={backtestResult.equityCurve} />
        </div>
      )}
    </div>
  );
}

export default Backtesting;
