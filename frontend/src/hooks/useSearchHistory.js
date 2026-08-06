import { useState, useEffect } from 'react';

const STORAGE_KEY = 'search_history';

export function useSearchHistory() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      setHistory(JSON.parse(stored));
    }
  }, []);

  const addSearch = (query) => {
    const newHistory = [query, ...history.filter(h => h !== query)].slice(0, 10);
    setHistory(newHistory);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newHistory));
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  return { history, addSearch, clearHistory };
}
