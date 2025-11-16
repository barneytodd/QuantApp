import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

/**
 * Helper to get environment variables, preferring runtime config if available.
 * Falls back to process.env for local development.
 */
function getEnvVar(key, fallback) {
  if (window.RUNTIME_CONFIG && window.RUNTIME_CONFIG[key] !== undefined) {
    return window.RUNTIME_CONFIG[key];
  }
  return process.env[key] || fallback;
}

// Fetch runtime config and only then render the app
fetch("/config/runtime.json")
  .then(res => {
    if (!res.ok) throw new Error("Runtime config not found");
    return res.json();
  })
  .then(cfg => {
    window.RUNTIME_CONFIG = cfg;

    // Set global env variable after runtime config is loaded
    window.REACT_APP_BACKEND_PORT = getEnvVar('REACT_APP_BACKEND_PORT', '8000');

    // Render the app
    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  })
  .catch(() => {
    // Fallback for local development
    window.REACT_APP_BACKEND_PORT = getEnvVar('REACT_APP_BACKEND_PORT', '8000');

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  });

// Optional: performance metrics
reportWebVitals();
