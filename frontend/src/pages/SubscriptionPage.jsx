import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SubscriptionPage = () => {
  const [plan, setPlan] = useState('monthly');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      features: ['Basic search', 'Limited cases', 'Community support']
    },
    {
      id: 'monthly',
      name: 'Monthly',
      price: 29.99,
      features: ['Full search', 'Unlimited cases', 'Priority support', 'Citation tools']
    },
    {
      id: 'yearly',
      name: 'Yearly',
      price: 299.99,
      features: ['Everything in Monthly', 'API access', 'Bulk downloads', 'Custom alerts']
    }
  ];

  const handleSubscribe = async (selectedPlan) => {
    setLoading(true);
    try {
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: selectedPlan })
      });
      const data = await response.json();
      if (data.success) {
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Subscription error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8">Choose Your Plan</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((planItem) => (
          <div
            key={planItem.id}
            className={`border rounded-lg p-6 ${
              plan === planItem.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            }`}
          >
            <h2 className="text-xl font-bold mb-2">{planItem.name}</h2>
            <p className="text-3xl font-bold mb-4">
              ${planItem.price}
              {planItem.price > 0 && <span className="text-sm font-normal">/month</span>}
            </p>
            <ul className="space-y-2 mb-6">
              {planItem.features.map((feature, index) => (
                <li key={index} className="flex items-center text-sm">
                  <span className="text-green-500 mr-2">✓</span>
                  {feature}
                </li>
              ))}
            </ul>
            <button
              onClick={() => handleSubscribe(planItem.id)}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Subscribe'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SubscriptionPage;
