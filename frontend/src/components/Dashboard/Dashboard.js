import { useEffect, useState } from "react";
import Select from "react-select";
import Chart from "./chart/Chart";
import ChartLegend from "./chart/ChartLegend";
import Slider from "./Slider";
import MetricCard from "./MetricCard";

// create app dashboard
function Dashboard() {

  // intialise and set variables used in dashboard
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  
  const [ohlcv, setOhlcv] = useState([]);
  const [metrics, setMetrics] = useState({});
  
  const [shortSMAPeriod, setShortPeriod] = useState(20); 
  const [longSMAPeriod, setLongPeriod] = useState(50);   
  const [emaPeriod, setEMAPeriod] = useState(20);  
  const [bollingerPeriod, setBollingerPeriod] = useState(20);

  const [bollingerMultiplier, setBollingerMultiplier] = useState(2);
  
  const [showEMA, setShowEMA] = useState(false);
  const [showBollinger, setShowBollinger] = useState(false);
  const [showShortSMA, setShowShortSMA] = useState(false);
  const [showLongSMA, setShowLongSMA] = useState(false);

  // get available ticker symbols from backend
  useEffect(() => {
    fetch("http://localhost:8000/api/symbols")
      .then(res => res.json())
      .then(data => {
        setSymbols(data.map(s => ({ value: s, label: s })));
        setSelectedSymbol({ value: data[0], label: data[0] }); // default first symbol
      });
  }, []);

  // get price data and calculated metrics from backend
  useEffect(() => {
    if (!selectedSymbol) return;

    fetch(`http://localhost:8000/api/ohlcv/${selectedSymbol?.value}?limit=200`)
      .then(res => res.json())
      .then(data => { 
        setOhlcv(data || []); 
      });

    fetch(`http://localhost:8000/api/metrics/${selectedSymbol?.value}`)
      .then(res => res.json())
      .then(data => setMetrics(data));
  }, [selectedSymbol]);

  // build dashboard
  return (
    <div className="p-4 space-y-4">

      {/* Symbol selector */}
      <div className="w-60">
        <h3 className="text-xl font-bold mb-2">View data for:</h3>
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

      {/* Chart and legend */}
      <div className="bg-white rounded-2xl shadow p-4">
        <h2 className="text-xl font-bold mb-2">{selectedSymbol?.value} Price Chart</h2>

        <div className="flex flex-wrap items-center gap-6 mb-4">
          <ChartLegend
            series={[
              { label: "Price", color: "#26a69a" },
              { label: "Short SMA", color: "#ff9900", checkbox: true, checked: showShortSMA, onChange: () => setShowShortSMA(!showShortSMA) },
              { label: "Long SMA", color: "#3366ff", checkbox: true, checked: showLongSMA, onChange: () => setShowLongSMA(!showLongSMA) },
              { label: "EMA", color: "#ff33cc", checkbox: true, checked: showEMA, onChange: () => setShowEMA(!showEMA) },
              { label: "Bollinger Bands", color: "#999999", checkbox: true, checked: showBollinger, onChange: () => setShowBollinger(!showBollinger) }
            ]}
          />
        </div>

        <Chart
          data={ohlcv}
          shortSMAPeriod={shortSMAPeriod}
          longSMAPeriod={longSMAPeriod}
          emaPeriod={emaPeriod}
          bollingerPeriod={bollingerPeriod}
          showShortSMA={showShortSMA}
          showLongSMA={showLongSMA}
          showEMA={showEMA}
          showBollinger={showBollinger}
          bollingerMultiplier={bollingerMultiplier}
        />
      </div>

      {/* Controls */}
      <div className="bg-white rounded-2xl shadow p-4">
        <h3 className="text-lg font-bold mb-2">Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Slider label="Short SMA Period" value={shortSMAPeriod} min={5} max={50} onChange={setShortPeriod} />
          <Slider label="Long SMA Period" value={longSMAPeriod} min={20} max={200} onChange={setLongPeriod} />
          <Slider label="EMA Period" value={emaPeriod} min={5} max={50} onChange={setEMAPeriod} />
          <Slider label="Bollinger Bands Period" value={bollingerPeriod} min={5} max={50} onChange={setBollingerPeriod} />
          <Slider label="Bollinger Bands Std Multiplier" value={bollingerMultiplier} min={1.5} max={3} step={0.1} onChange={setBollingerMultiplier} />
        </div>
      </div>

      {/* Metrics panel */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Annualised Return" value={metrics.mean_return} />
        <MetricCard label="Volatility" value={metrics.annualised_volatility} />
        <MetricCard label="Sharpe Ratio" value={metrics.sharpe_ratio} />
        <MetricCard label="Max Drawdown" value={metrics.max_drawdown} />
      </div>

    </div>
  );
}

export default Dashboard;
