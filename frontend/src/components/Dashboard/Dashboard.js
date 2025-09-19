  import { useEffect, useState } from "react";
  import Select from "react-select";
  import Chart from "./chart/Chart";
  import ChartLegend from "./chart/ChartLegend";
  import Slider from "./Slider";
  import MetricCard from "./MetricCard";
  import { Option, MenuList } from "../select/CustomSelectComponents"

  // create app dashboard
  function Dashboard() {

    // intialise and set variables used in dashboard
    const [symbols, setSymbols] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState(null);

    const [uploadSymbols, setUploadSymbols] = useState([]);
    const [selectedUploadSymbols, setSelectedUploadSymbols] = useState([]);
    
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

    // get available ticker symbols to upload data
    useEffect(() => {
      fetch("http://localhost:8000/api/fetch_symbols")
        .then(res => res.json())
        .then(data => {
          setUploadSymbols(data.map(s => ({ value: s, label: s })));
        });
    }, []);

    // Handle multi-symbol "Upload/Insert" button click
    const handleUploadData = async () => {
      if (selectedUploadSymbols.length === 0) return;
      const symbolValues = selectedUploadSymbols.map(s => s.value);

      try {
        const res = await fetch("http://localhost:8000/api/ohlcv/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ symbols: symbolValues, period: "1y" }),
        });
        const result = await res.json();
        console.log("Upload result:", result);
        alert(`Data uploaded for ${symbolValues.length} symbols`);
      } catch (err) {
        console.error(err);
        alert("Error uploading data");
      }
    };
    
    // build dashboard
    return (
      <div className="p-4 space-y-4">

        {/* Top bar: symbol selector + upload button */}
        <div className="flex justify-between items-start gap-4 mb-4">
          
          {/* Single-symbol selector */}
          <div className="w-60">
            <h3 className="text-xl font-bold mb-2">View data for:</h3>
            <Select
              options={symbols}
              value={selectedSymbol}
              onChange={setSelectedSymbol}
              isSearchable
              placeholder="Select a ticker symbol"
              menuPortalTarget={document.body}   
              styles={{ menuPortal: (base) => ({ ...base, zIndex: 9999 }) }}
            />
          </div>

          {/* Multi-symbol upload */}
          <div className="w-80 bg-white rounded-2xl shadow p-4">
            <h3 className="text-lg font-bold mb-2">Upload / Insert Data</h3>

            <Select
              options={uploadSymbols}
              value={selectedUploadSymbols}
              onChange={setSelectedUploadSymbols}
              isMulti
              isSearchable
              closeMenuOnSelect={false}
              hideSelectedOptions={false}
              menuShouldScrollIntoView={false}
              placeholder="Select ticker symbols"
              menuPortalTarget={document.body}
              menuPosition="fixed"
              components={{ Option, MenuList }}
              styles={{ menuPortal: (base) => ({ ...base, zIndex: 9999 }) }}
            />

            <button
              className="mt-2 w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={handleUploadData}
              disabled={selectedUploadSymbols.length === 0}
            >
              Upload / Insert
            </button>
          </div>

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
