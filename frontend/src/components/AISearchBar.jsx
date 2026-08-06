import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Loader2, Sparkles, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function AISearchBar({ size = 'default', className = '' }) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const wrapperRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchSuggestions = async (q) => {
    if (q.length < 2) { setSuggestions([]); return; }
    try {
      const res = await fetch(`${API}/api/suggest?q=${encodeURIComponent(q)}`);
      if (res.ok) setSuggestions(await res.json());
    } catch (e) { console.error(e); }
  };

  const debounceRef = useRef(null);
  const onChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => fetchSuggestions(val), 200);
    setShowSuggestions(true);
  };

  const onSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setShowSuggestions(false);
    navigate(`/search?q=${encodeURIComponent(query.trim())}`);
  };

  const onSuggestionClick = (s) => {
    setQuery(s);
    setShowSuggestions(false);
    navigate(`/search?q=${encodeURIComponent(s)}`);
  };

  const isLarge = size === 'large';

  return (
    <div ref={wrapperRef} className={`relative ${className}`}>
      <form onSubmit={onSubmit} className="relative">
        <Search className={`absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground ${isLarge ? 'w-5 h-5' : 'w-4 h-4'}`} />
        <input
          type="text"
          value={query}
          onChange={onChange}
          onFocus={() => query.length >= 2 && setShowSuggestions(true)}
          placeholder="Search cases, statutes, or ask a legal question..."
          className={`w-full bg-white dark:bg-background border rounded-full pl-10 pr-12 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-shadow ${
            isLarge ? 'py-3.5 text-base pr-14' : 'py-2.5 text-sm'
          }`}
        />
        {query && (
          <button type="button" onClick={() => { setQuery(''); setSuggestions([]); }} className="absolute right-10 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
            <X size={16} />
          </button>
        )}
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className={`absolute right-1.5 top-1/2 -translate-y-1/2 bg-primary hover:bg-primary/90 text-primary-foreground rounded-full flex items-center justify-center disabled:opacity-50 ${
            isLarge ? 'w-10 h-10' : 'w-8 h-8'
          }`}
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <ArrowRight size={16} />}
        </button>
      </form>

      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-background border rounded-xl shadow-lg z-50 overflow-hidden">
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => onSuggestionClick(s)}
              className="w-full text-left px-4 py-2.5 text-sm hover:bg-background flex items-center gap-2"
            >
              <Sparkles size={14} className="text-muted-foreground" /> {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
