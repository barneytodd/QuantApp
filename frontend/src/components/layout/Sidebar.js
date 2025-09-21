import { Link } from "react-router-dom";

export default function Sidebar({ isOpen, onClose }) {
  return (
    <div
      className={`fixed top-0 left-0 h-full w-64 bg-white shadow-lg transform transition-transform duration-300 z-50 ${
        isOpen ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      <div className="flex justify-between items-center p-4 border-b">
        <h2 className="text-lg font-bold">Menu</h2>
        <button onClick={onClose} className="text-gray-600 hover:text-gray-900 text-xl">
          ✕
        </button>
      </div>
      <nav className="flex flex-col p-4 gap-4">
        <Link to="/" onClick={onClose} className="hover:text-teal-600 font-medium">Dashboard</Link>
        <Link to="/backtesting" onClick={onClose} className="hover:text-teal-600 font-medium">Backtesting</Link>
        <Link to="/simulator" onClick={onClose} className="hover:text-teal-600 font-medium">Trading Simulator</Link>
        <Link to="/portfolio" onClick={onClose} className="hover:text-teal-600 font-medium">Portfolio Analysis</Link>
      </nav>
    </div>
  );
}
