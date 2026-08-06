import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { searchWithAI } from '@/services/aiSearch';

const AISearchBar = ({ onResults }) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    const results = await searchWithAI(query);
    onResults(results);
    setLoading(false);
  };

  const handleSuggestion = async (s) => {
    setQuery(s);
    setSuggestions([]);
    setLoading(true);
    const results = await searchWithAI(s);
    onResults(results);
    setLoading(false);
  };

  return (
    <div className="w-full">
      <div className="flex gap-2">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search with AI..."
          className="flex-1"
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <Button onClick={handleSearch} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </div>
      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {suggestions.map((s, i) => (
            <Badge key={i} className="cursor-pointer" onClick={() => handleSuggestion(s)}>
              {s}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
};

export default AISearchBar;
