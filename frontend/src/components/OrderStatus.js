import React, { useState } from 'react';
import axios from 'axios';

function OrderStatus() {
  const [orderId, setOrderId] = useState('');
  const [orderDetails, setOrderDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!orderId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/orders/${orderId}`);
      setOrderDetails(response.data);
    } catch (err) {
      setError('Order not found or error checking status.');
      setOrderDetails(null);
    } finally {
      setLoading(false);
    }
  };

  const getStatusClass = (status) => {
    switch(status) {
      case 'pending': return 'status-pending';
      case 'processing': return 'status-processing';
      case 'completed': return 'status-completed';
      case 'failed': return 'status-failed';
      default: return '';
    }
  };

  return (
    <div>
      <h2>Check Order Status</h2>
      <div className="status-checker">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="orderId">Order ID:</label>
            <input
              type="text"
              id="orderId"
              value={orderId}
              onChange={(e) => setOrderId(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <button type="submit" disabled={loading}>
              {loading ? 'Checking...' : 'Check Status'}
            </button>
          </div>
        </form>
        
        {error && <div className="alert alert-error">{error}</div>}
        
        {orderDetails && (
          <div className="status-result">
            <h3>Order #{orderDetails.order_id}</h3>
            <p>Customer: {orderDetails.customer_name}</p>
            <p>Date: {new Date(orderDetails.created_at).toLocaleString()}</p>
            <p>
              Status: <span className={getStatusClass(orderDetails.status)}>
                {orderDetails.status.toUpperCase()}
              </span>
            </p>
            <p>Total: ${orderDetails.total_amount.toFixed(2)}</p>
            
            <h4>Items:</h4>
            <ul>
              {orderDetails.items.map((item, index) => (
                <li key={index}>
                  {item.quantity}x {item.name} - ${(item.price * item.quantity).toFixed(2)}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default OrderStatus;