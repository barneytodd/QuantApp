import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Sidebar from "./components/layout/Sidebar";
import Dashboard from "./pages/Dashboard/Dashboard";
import Backtesting from "./pages/Backtesting/Backtesting";
import TradingSimulatorPage from "./pages/TradingSimulator/TradingSimulator";
import PortfolioBuilder from "./pages/PortfolioAnalysis/PortfolioAnalysis";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <Router>
      {/* Menu Button */}
      <button
        className="fixed top-4 left-4 z-50 bg-teal-500 text-white p-2 rounded-lg shadow"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        ☰ Menu
      </button>

      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-25 z-20"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className={`transition-all duration-300 ${
        sidebarOpen ? "ml-32" : "ml-0"
      } pl-32`}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/backtesting" element={<Backtesting />} />
          <Route path="/simulator" element={<TradingSimulatorPage />} />
          <Route path="/portfolio" element={<PortfolioBuilder />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
