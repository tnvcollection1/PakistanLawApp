import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const StatutesSearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    year: '',
    category: '',
    court: ''
  });
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const params = new URLSearchParams({ q: query, ...filters });
      const response = await fetch(`/api/statutes/search?${params}`);
      const data = await response.json();
      setResults(data.statutes || []);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Statute Search</h1>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search statutes..."
            className="flex-1 border rounded-md px-4 py-2"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      <div className="space-y-4">
        {results.length === 0 && !loading && (
          <p className="text-gray-500">No results found</p>
        )}
        {results.map((statute) => (
          <div key={statute.id} className="border rounded-lg p-4 hover:shadow-md transition">
            <h3 className="text-lg font-semibold">
              <a href={`/statute/${statute.id}`} className="text-blue-600 hover:underline">
                {statute.title}
              </a>
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Year: {statute.year} | Category: {statute.category}
            </p>
            <p className="text-gray-700 mt-2 line-clamp-3">{statute.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StatutesSearchPage;
