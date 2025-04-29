import React, { useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import ProductList from './components/ProductList';
import OrderForm from './components/OrderForm';
import OrderStatus from './components/OrderStatus';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Sweet Delights Bakery</h1>
          <nav>
            <ul>
              <li><Link to="/">Products</Link></li>
              <li><Link to="/order">Place Order</Link></li>
              <li><Link to="/status">Check Order</Link></li>
            </ul>
          </nav>
        </header>
        
        <main>
          <Routes>
            <Route path="/" element={<ProductList />} />
            <Route path="/order" element={<OrderForm />} />
            <Route path="/status" element={<OrderStatus />} />
          </Routes>
        </main>
        
        <footer>
          <p>© 2025 Sweet Delights Bakery - Containerized with Docker</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;