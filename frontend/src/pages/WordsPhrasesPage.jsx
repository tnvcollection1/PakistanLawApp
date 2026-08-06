import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  MessageSquare, Search, ChevronRight, ChevronLeft, Loader2,
  AlertCircle, BookOpen
} from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

export default function WordsPhrasesPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [error, setError] = useState(null);
  const limit = 50;

  const searchWords = async (q, p = 1) => {
    if (!q.trim()) {
      setResults([]);
      setTotal(0);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ q, page: p, limit });
      const res = await fetch(`${API}/search/words?${params}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResults(data.data || []);
      setTotal(data.total || 0);
      setPage(p);
    } catch (e) {
      setError(e.message);
      setResults([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setQuery(q);
      searchWords(q, 1);
    }
  }, [searchParams]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchParams({ q: query });
    }
  };

  const pages = Math.ceil(total / limit);

  return (
    <div className="min-h-screen bg-background dark:bg-background" data-testid="words-phrases-page">
      <div className="bg-white dark:bg-background border-b border-muted dark:border-border">
        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-slate-900 dark:text-primary-foreground flex items-center gap-3" data-testid="words-phrases-title">
            <MessageSquare className="text-primary" size={28} />
            Words & Phrases
          </h1>
          <p className="text-sm text-muted-foreground dark:text-muted-foreground mt-1">
            Legal definitions and interpretations
          </p>
        </div>
      </div>

      <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
        <form onSubmit={handleSearch} className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-4 mb-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <Input
                placeholder="Search words or phrases..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-10 text-base bg-background dark:bg-background"
                data-testid="words-search-input"
              />
            </div>
            <Button type="submit" className="bg-background hover:bg-card" data-testid="words-search-btn">
              Search
            </Button>
          </div>
        </form>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-6 flex items-center gap-3">
            <AlertCircle className="text-red-500" size={20} />
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="p-12 text-center">
            <Loader2 size={32} className="animate-spin text-slate-800 dark:text-foreground mx-auto mb-3" />
            <p className="text-muted-foreground dark:text-muted-foreground">Searching...</p>
          </div>
        ) : results.length === 0 && query ? (
          <div className="p-12 text-center">
            <BookOpen size={48} className="text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground dark:text-muted-foreground">No results for "{query}"</p>
          </div>
        ) : (
          <>
            <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border overflow-hidden">
              <div className="p-4 border-b border-muted dark:border-border flex items-center justify-between">
                <h2 className="font-semibold text-slate-800 dark:text-primary-foreground">
                  {total.toLocaleString()} results
                </h2>
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {results.map((result, idx) => (
                  <div
                    key={idx}
                    className="p-4 hover:bg-background dark:hover:bg-card/50 transition-colors"
                  >
                    <p className="font-semibold text-slate-900 dark:text-primary-foreground text-lg">
                      {result.phrase || result.word}
                    </p>
                    <p className="text-muted-foreground dark:text-muted-foreground text-sm mt-1">
                      {result.definition || result.meaning || 'No definition available'}
                    </p>
                    {result.source_case && (
                      <p className="text-xs text-primary mt-2">
                        Source: {result.source_case}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {pages > 1 && (
              <div className="mt-6 flex items-center justify-between">
                <p className="text-sm text-muted-foreground dark:text-muted-foreground">
                  Page {page} of {pages}
                </p>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => searchWords(query, page - 1)}>
                    <ChevronLeft size={16} className="mr-1" /> Previous
                  </Button>
                  <Button variant="outline" size="sm" disabled={page >= pages} onClick={() => searchWords(query, page + 1)}>
                    Next <ChevronRight size={16} className="ml-1" />
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
