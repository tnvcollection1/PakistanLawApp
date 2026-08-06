import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Sparkles, X, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";

export default function AISearchBar({ onSearch, placeholder = "Search cases, statutes, judges..." }) {
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  const handleInputChange = async (e) => {
    const value = e.target.value;
    setQuery(value);
    
    if (value.length > 2) {
      // In production, fetch suggestions from backend
      setSuggestions([
        `${value} in constitutional law`,
        `${value} related cases`,
        `${value} statutory interpretation`
      ]);
    } else {
      setSuggestions([]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setIsLoading(true);
      onSearch?.(query.trim());
      setIsLoading(false);
      setSuggestions([]);
    }
  };

  const clearSearch = () => {
    setQuery("");
    setSuggestions([]);
  };

  return (
    <div className="relative w-full max-w-2xl">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          <Search className="absolute left-3 w-4 h-4 text-slate-400" />
          <Input
            type="text"
            placeholder={placeholder}
            className="pl-10 pr-10 py-2 bg-slate-800/60 border-slate-700 text-white placeholder:text-slate-500 focus:border-sky-500 focus:ring-sky-500/20"
            value={query}
            onChange={handleInputChange}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setTimeout(() => setIsFocused(false), 200)}
          />
          {query && (
            <button
              type="button"
              onClick={clearSearch}
              className="absolute right-10 p-1 text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            type="submit"
            className="absolute right-2 p-1.5 rounded-md bg-sky-600 hover:bg-sky-700 text-white transition-colors"
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4" />
            )}
          </button>
        </div>
      </form>

      <AnimatePresence>
        {isFocused && suggestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 right-0 mt-1 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50 overflow-hidden"
          >
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                className="w-full px-4 py-2.5 text-left text-sm text-slate-300 hover:bg-slate-700/50 transition-colors flex items-center gap-2"
                onClick={() => {
                  setQuery(suggestion);
                  setSuggestions([]);
                  onSearch?.(suggestion);
                }}
              >
                <Sparkles className="w-3 h-3 text-sky-400" />
                {suggestion}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
