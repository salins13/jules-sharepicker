import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TradingViewWidget from 'react-tradingview-widget';
import './App.css';

function App() {
  const [scanResults, setScanResults] = useState({ bullish: [], bearish: [] });
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/scan');
        setScanResults(response.data);
      } catch (error) {
        console.error("Error fetching scan results:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every minute

    return () => clearInterval(interval);
  }, []);

  const handleStockSelect = (symbol) => {
    // yfinance symbols are like 'RELIANCE.NS', but TradingView expects 'NSE:RELIANCE'
    const formattedSymbol = symbol.replace('_NS', '').replace('.', ':');
    setSelectedSymbol(formattedSymbol);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Intraday Stock Screener</h1>
      </header>
      <div className="dashboard-container">
        <div className="watchlist-container">
          <h2>Bullish Stocks</h2>
          <table>
            <thead>
              <tr>
                <th>Stock</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {scanResults.bullish.map(stock => (
                <tr key={stock.stock} onClick={() => handleStockSelect(stock.stock)}>
                  <td>{stock.stock}</td>
                  <td>{stock.score.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <h2>Bearish Stocks</h2>
          <table>
            <thead>
              <tr>
                <th>Stock</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {scanResults.bearish.map(stock => (
                <tr key={stock.stock} onClick={() => handleStockSelect(stock.stock)}>
                  <td>{stock.stock}</td>
                  <td>{stock.score.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="chart-container">
          <TradingViewWidget
            symbol={selectedSymbol}
            autosize
          />
        </div>
      </div>
    </div>
  );
}

export default App;
