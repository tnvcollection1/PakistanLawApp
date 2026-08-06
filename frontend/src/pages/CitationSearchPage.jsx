import React, { useState } from 'react';
import { Search, Filter, BookOpen, Scale } from 'lucide-react';
import { searchCases } from '../api/api';

export default function CitationSearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setHasSearched(true);
    try {
      const data = await searchCases(query, page, 20);
      setResults(data.data || []);
      setTotal(data.total || 0);
    } catch (e) {
      console.error('Search failed:', e);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-[#1a365d] mb-6 flex items-center gap-2">
        <Search size={28} />
        Citation Search
      </h1>

      <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Search by citation, title, parties, or keywords..."
              className="w-full border rounded-lg px-4 py-3 pl-10 focus:outline-none focus:ring-2 focus:ring-[#1a365d]"
            />
            <Search className="absolute left-3 top-3.5 text-gray-400" size={18} />
          </div>
          <button
            onClick={handleSearch}
            disabled={loading}
            className="bg-[#1a365d] text-white px-6 py-3 rounded-lg hover:bg-[#234e8e] disabled:opacity-50 flex items-center gap-2"
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

      {!loading && hasSearched && results.length === 0 && (
        <div className="text-center py-12">
          <BookOpen className="mx-auto h-12 w-12 text-gray-300 mb-4" />
          <p className="text-gray-500 text-lg">No cases found matching your search.</p>
          <p className="text-gray-400 text-sm mt-2">Try different keywords or check your spelling.</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-4 border-b flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Found {total.toLocaleString()} results
            </p>
          </div>
          <div className="divide-y">
            {results.map((case_) => (
              <div key={case_.id} className="p-4 hover:bg-gray-50 transition">
                <a href={`/cases/${case_.id}`} className="text-lg font-semibold text-[#1a365d] hover:underline">
                  {case_.citation || case_.title}
                </a>
                <p className="text-sm text-gray-500 mt-1">
                  {case_.court} • {case_.year} • {case_.judges}
                </p>
                {case_.headnotes && (
                  <p className="text-sm text-gray-600 mt-2 line-clamp-2">{case_.headnotes}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
