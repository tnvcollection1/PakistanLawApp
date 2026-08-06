import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const SearchSuggestions = ({ query, onSelect }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!query || query.length < 2) {
      setSuggestions([]);
      return;
    }

    const fetchSuggestions = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleSelect = (suggestion) => {
    if (onSelect) {
      onSelect(suggestion);
    } else {
      navigate(`/search?q=${encodeURIComponent(suggestion)}`);
    }
  };

  if (!query || query.length < 2) return null;

  return (
    <div className="absolute z-50 w-full bg-white border border-gray-200 rounded-md shadow-lg mt-1">
      {loading && (
        <div className="px-4 py-2 text-sm text-gray-500">Loading...</div>
      )}
      {suggestions.length === 0 && !loading && (
        <div className="px-4 py-2 text-sm text-gray-500">No suggestions found</div>
      )}
      {suggestions.map((suggestion, index) => (
        <button
          key={index}
          className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm"
          onClick={() => handleSelect(suggestion)}
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
};

export default SearchSuggestions;
