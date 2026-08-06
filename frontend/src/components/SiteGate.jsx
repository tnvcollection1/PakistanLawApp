import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SiteGate = ({ onAccess }) => {
  const [accessCode, setAccessCode] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Simple access code validation
    if (accessCode === 'PLS2024') {
      localStorage.setItem('site_access', 'granted');
      if (onAccess) {
        onAccess();
      }
      navigate('/');
    } else {
      setError('Invalid access code. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">Pakistan Law Site</h1>
        <p className="text-gray-600 text-center mb-6">
          Please enter the access code to continue.
        </p>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <input
              type="password"
              value={accessCode}
              onChange={(e) => setAccessCode(e.target.value)}
              placeholder="Enter access code"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          {error && (
            <p className="text-red-500 text-sm mb-4">{error}</p>
          )}
          
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
          >
            Access Site
          </button>
        </form>
      </div>
    </div>
  );
};

export default SiteGate;
