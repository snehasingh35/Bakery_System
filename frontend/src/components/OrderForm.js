import React, { useState, useEffect } from 'react';
import axios from 'axios';

function OrderForm() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [customerName, setCustomerName] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [orderItems, setOrderItems] = useState([{ product_id: '', quantity: 1 }]);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [orderId, setOrderId] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get('/api/products');
        setProducts(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching products:', err);
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  const handleAddItem = () => {
    setOrderItems([...orderItems, { product_id: '', quantity: 1 }]);
  };

  const handleRemoveItem = (index) => {
    const newItems = [...orderItems];
    newItems.splice(index, 1);
    setOrderItems(newItems);
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...orderItems];
    newItems[index][field] = field === 'quantity' ? parseInt(value, 10) : value;
    setOrderItems(newItems);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Basic validation
    if (!customerName || !customerEmail || orderItems.length === 0) {
      setSubmitStatus('error');
      return;
    }
    
    // Filter out incomplete items
    const validItems = orderItems.filter(item => item.product_id && item.quantity > 0);
    
    if (validItems.length === 0) {
      setSubmitStatus('error');
      return;
    }
    
    try {
      const response = await axios.post('/api/orders', {
        customer_name: customerName,
        customer_email: customerEmail,
        items: validItems
      });
      
      setSubmitStatus('success');
      setOrderId(response.data.order_id);
    } catch (err) {
      console.error('Error placing order:', err);
      setSubmitStatus('error');
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (submitStatus === 'success' && orderId) {
    return (
      <div className="order-form">
        <div className="alert alert-success">
          Your order has been placed successfully!
        </div>
        <p>Order ID: <strong>{orderId}</strong></p>
        <p>You can check your order status using this ID.</p>
        <button onClick={() => setSubmitStatus(null)}>Place Another Order</button>
      </div>
    );
  }

  return (
    <div>
      <h2>Place Your Order</h2>
      <form className="order-form" onSubmit={handleSubmit}>
        {submitStatus === 'error' && (
          <div className="alert alert-error">
            Please fill all required fields correctly.
          </div>
        )}
        
        <div className="form-group">
          <label htmlFor="customerName">Your Name:</label>
          <input
            type="text"
            id="customerName"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="customerEmail">Email:</label>
          <input
            type="email"
            id="customerEmail"
            value={customerEmail}
            onChange={(e) => setCustomerEmail(e.target.value)}
            required
          />
        </div>
        
        <h3>Order Items</h3>
        {orderItems.map((item, index) => (
          <div key={index} className="form-group">
            <div className="item-selection">
              <select
                value={item.product_id}
                onChange={(e) => handleItemChange(index, 'product_id', e.target.value)}
                required
              >
                <option value="">Select a product</option>
                {products.map(product => (
                  <option key={product.id} value={product.id}>
                    {product.name} (${product.price.toFixed(2)})
                  </option>
                ))}
              </select>
              <input
                type="number"
                min="1"
                value={item.quantity}
                onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                required
              />
              
              {orderItems.length > 1 && (
                <button 
                  type="button" 
                  className="remove-item-btn"
                  onClick={() => handleRemoveItem(index)}
                >
                  Remove
                </button>
              )}
            </div>
          </div>
        ))}
        
        <div className="form-group">
          <button 
            type="button" 
            className="add-item-btn" 
            onClick={handleAddItem}
          >
            Add Another Item
          </button>
        </div>
        
        <div className="form-group">
          <button type="submit">Place Order</button>
        </div>
      </form>
    </div>
  );
}

export default OrderForm;