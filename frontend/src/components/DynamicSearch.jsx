import React, { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { Link } from "react-router-dom";

export default function DynamicSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }
    const timeout = setTimeout(() => {
      performSearch();
    }, 300);
    return () => clearTimeout(timeout);
  }, [query]);

  const performSearch = () => {
    setIsSearching(true);
    // Mock search results
    setResults([
      { id: 1, title: `Case related to ${query}`, type: "case" },
      { id: 2, title: `Statute on ${query}`, type: "statute" },
      { id: 3, title: `Article about ${query}`, type: "article" },
    ]);
    setIsSearching(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    performSearch();
  };

  return (
    <div className="relative w-full max-w-2xl">
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search cases, statutes, articles..."
            className="pl-8 w-full"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </form>
      {results.length > 0 && (
        <div className="absolute top-full left-0 right-0 bg-background border rounded-md shadow-lg z-50 mt-1">
          <ul className="py-2">
            {results.map((result) => (
              <li key={result.id}>
                <Link
                  to={`/${result.type}s/${result.id}`}
                  className="block px-4 py-2 hover:bg-accent hover:text-accent-foreground"
                >
                  <span className="font-medium">{result.title}</span>
                  <span className="ml-2 text-xs text-muted-foreground capitalize">
                    {result.type}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
      {isSearching && (
        <div className="absolute top-full left-0 right-0 bg-background border rounded-md shadow-lg z-50 mt-1 p-4 text-center">
          Searching...
        </div>
      )}
    </div>
  );
}
