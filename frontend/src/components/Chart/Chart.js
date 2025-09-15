import React, { useEffect, useRef } from "react";
import { createChart, CandlestickSeries, LineSeries, createSeriesMarkers } from "lightweight-charts";
import { computeSMA, computeEMA, detectCrossovers, computeBollingerBands } from "../../utils/indicators";


// Build the price analysis chart
function Chart({ data, shortSMAPeriod, longSMAPeriod, emaPeriod, bollingerPeriod, showShortSMA, showLongSMA, showEMA, showBollinger, bollingerMultiplier }) {
  const containerRef = useRef(null);

  // refs to hold the chart + series 
  const chartRef = useRef(null);
  const candleRef = useRef(null);
  const shortSMARef = useRef(null);
  const longSMARef = useRef(null);
  const emaRef = useRef(null);
  const lowerBollingerRef = useRef(null);
  const midBollingerRef = useRef(null);
  const upperBollingerRef = useRef(null);
  const proxyRef = useRef(null);
  const markersRef = useRef(null);
  const shortSMADataRef = useRef(null);
  const longSMADataRef = useRef(null);

  useEffect(() => {

    if (!containerRef.current) return;

    if (!data) return;

    // create the chart
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: "#ffffff" },
        textColor: "#333",
      },
      grid: {
        vertLines: { color: "#eee" },
        horzLines: { color: "#eee" },
      },
      crosshair: {
        mode: 1,
      },
      timeScale: {
        borderColor: "#ccc",
      },
    });

    // create the price series
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderDownColor: "#ef5350",
      borderUpColor: "#26a69a",
      wickDownColor: "#ef5350",
      wickUpColor: "#26a69a",
    });

     // Long-term SMA (20-day)
    const shortSMASeries = chart.addSeries(LineSeries, {
      color: "#ff9900",
      lineWidth: 2,
    });

    // Long-term SMA (50-day)
    const longSMASeries = chart.addSeries(LineSeries, {
      color: "#3366ff",
      lineWidth: 2,
    });

    // EMA series
    const emaSeries = chart.addSeries(LineSeries, {
      color: "#ff33cc",
      lineWidth: 2,
    })

    // lower bollinger band
    const lowerBollingerSeries = chart.addSeries(LineSeries, {
      color: "#999999",
      lineWidth: 2,
    })
    
    // mid bollinger band (mean)
    const midBollingerSeries = chart.addSeries(LineSeries, {
      color: "#666666",
      lineWidth: 2,
    })

    // upper bollinger band
    const upperBollingerSeries = chart.addSeries(LineSeries, {
      color: "#999999",
      lineWidth: 2,
    })

    // proxy series for buy/sell markers
    const proxySeries = chart.addSeries(LineSeries, {
      color: 'transparent',
      lineWidth: 2,
    });

    // buy/sell markers
    const seriesMarkers = createSeriesMarkers(proxySeries);
    
    // store refs
    chartRef.current = chart;
    candleRef.current = candleSeries;
    shortSMARef.current = shortSMASeries;
    longSMARef.current = longSMASeries;
    emaRef.current = emaSeries;
    lowerBollingerRef.current = lowerBollingerSeries;
    midBollingerRef.current = midBollingerSeries;
    upperBollingerRef.current = upperBollingerSeries;
    proxyRef.current = proxySeries;
    markersRef.current = seriesMarkers;

    // handle resize
    const ro = new ResizeObserver(() => {
      chart.applyOptions({ width: containerRef.current.clientWidth });
    });
    ro.observe(containerRef.current);

    return () => {
      ro.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [data]);

  // update data & series when props change
  useEffect(() => {
    if (!chartRef.current || !data || data.length === 0) return;

    // format price data
    const formattedData = Array.isArray(data) ? data.map(d => ({
      time: d.date.slice(0, 10), 
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close ? d.close : d.value,
    })) : [];


    // set data for analysis lines
    if (showShortSMA) {
      shortSMADataRef.current = computeSMA(formattedData, shortSMAPeriod);
      shortSMARef.current.setData(shortSMADataRef.current.filter(d => d.value !== null));
    }
    else {
      shortSMARef.current.setData([]);
    };

    if (showLongSMA) {
      longSMADataRef.current = computeSMA(formattedData, longSMAPeriod);
      longSMARef.current.setData(longSMADataRef.current.filter(d => d.value !== null));
    }
    else {
      longSMARef.current.setData([]);
    };

    if (showEMA) {
      const emaData = computeEMA(formattedData, emaPeriod);
      emaRef.current.setData(emaData.filter(d => d.value !== null));
    }
    else {
      emaRef.current.setData([]);
    };

    if (showBollinger) {
      const bollingerData = computeBollingerBands(formattedData, bollingerPeriod, bollingerMultiplier);
      lowerBollingerRef.current.setData(bollingerData.map(d => ({time: d.time, value:d.lower})).filter(d => d.value !== null));
      midBollingerRef.current.setData(bollingerData.map(d => ({time: d.time, value:d.middle})).filter(d => d.value !== null));
      upperBollingerRef.current.setData(bollingerData.map(d => ({time: d.time, value:d.upper})).filter(d => d.value !== null))
    }
    else {
      lowerBollingerRef.current.setData([]);
      midBollingerRef.current.setData([]);
      upperBollingerRef.current.setData([])
    }


    // Add buy/sell markers
    if (showLongSMA && showShortSMA) {
      // proxy data for buy/sell markers
      const proxyData = formattedData.map((d, i) => ({
        time: d.time.slice(0, 10),
        value: i < longSMAPeriod ? d.close : longSMADataRef.current[i].value,
      }));

      proxyRef.current.setData(proxyData);

      // calculate buy/sell markers at points where short and long SMA lines cross
      const signals = detectCrossovers(shortSMADataRef.current, longSMADataRef.current, data, shortSMAPeriod, longSMAPeriod);

      const markers = signals.map(signal => ({
        time: signal.time,
        position: signal.type === "buy" ? "belowBar" : "aboveBar",
        color: signal.type === "buy" ? "green" : "red",
        shape: signal.type === "buy" ? "arrowUp" : "arrowDown",
        text: signal.type.toUpperCase(),
      }));
        
      markersRef.current.setMarkers(markers);
    }
    else {
      markersRef.current.setMarkers([])
    }

    // set price data
    console.log(formattedData);
    candleRef.current.setData(formattedData);
    
    chartRef.current.timeScale().fitContent();

  }, [data, shortSMAPeriod, longSMAPeriod, emaPeriod, bollingerPeriod, showShortSMA, showLongSMA, showEMA, showBollinger, bollingerMultiplier]);


  return <div ref={containerRef} className="w-full h-[400px]" />;
}

export default Chart;
