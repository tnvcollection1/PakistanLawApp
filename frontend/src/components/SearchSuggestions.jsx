import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";

export default function SearchSuggestions({ query, onSelect }) {
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    if (query.length < 2) {
      setSuggestions([]);
      return;
    }
    // Mock suggestions for now
    setSuggestions([
      { id: 1, title: `Case about ${query}`, type: "case" },
      { id: 2, title: `Statute ${query}`, type: "statute" },
      { id: 3, title: `Article on ${query}`, type: "article" },
    ]);
  }, [query]);

  if (!query || suggestions.length === 0) return null;

  return (
    <div className="absolute top-full left-0 right-0 bg-background border rounded-md shadow-lg z-50 mt-1">
      <ul className="py-2">
        {suggestions.map((suggestion) => (
          <li key={suggestion.id}>
            <button
              className="w-full text-left px-4 py-2 hover:bg-accent hover:text-accent-foreground"
              onClick={() => onSelect(suggestion)}
            >
              <span className="font-medium">{suggestion.title}</span>
              <span className="ml-2 text-xs text-muted-foreground capitalize">
                {suggestion.type}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
