import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Must match export in App.js
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);