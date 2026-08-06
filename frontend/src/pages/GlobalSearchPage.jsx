import React, { useState } from 'react';
import { Search, BookOpen, Filter } from 'lucide-react';

export default function GlobalSearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/search/caselaws?q=${encodeURIComponent(query)}&page=1&limit=20`);
      const data = await res.json();
      setResults(data.data || []);
    } catch (e) {
      console.error('Search failed:', e);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-[#1a365d] mb-6 flex items-center gap-2">
        <Search size={28} />
        Global Search
      </h1>

      <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search across all 369,810+ cases..."
              className="w-full border rounded-lg px-4 py-3 pl-10 focus:outline-none focus:ring-2 focus:ring-[#1a365d]"
            />
            <Search className="absolute left-3 top-3.5 text-gray-400" size={18} />
          </div>
          <button
            onClick={handleSearch}
            disabled={loading}
            className="bg-[#1a365d] text-white px-6 py-3 rounded-lg hover:bg-[#234e8e] disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#1a365d]"></div>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b">
            <p className="text-sm text-gray-500">{results.length} results found</p>
          </div>
          <div className="divide-y">
            {results.map((case_) => (
              <div key={case_.id} className="p-4 hover:bg-gray-50">
                <a href={`/cases/${case_.id}`} className="text-lg font-semibold text-[#1a365d] hover:underline">
                  {case_.citation || case_.title}
                </a>
                <p className="text-sm text-gray-500">{case_.court} • {case_.year}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && query && results.length === 0 && (
        <div className="text-center py-12">
          <BookOpen className="mx-auto h-12 w-12 text-gray-300 mb-4" />
          <p className="text-gray-500">No results found. Try different keywords.</p>
        </div>
      )}
    </div>
  );
}
