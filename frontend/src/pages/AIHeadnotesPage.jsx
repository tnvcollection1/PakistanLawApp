import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Sparkles, Search, ChevronRight, ChevronLeft, Scale,
  Loader2, BookOpen, AlertCircle, Filter
} from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

export default function AIHeadnotesPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const limit = 20;

  const searchHeadnotes = useCallback(async (q, p = 1) => {
    if (!q.trim()) {
      setResults([]);
      setTotal(0);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ q, page: p, limit });
      if (filter !== 'all') params.append('filter', filter);
      const res = await fetch(`${API}/search/headnotes?${params}`);
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
  }, [filter]);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setQuery(q);
      searchHeadnotes(q, 1);
    }
  }, [searchParams, searchHeadnotes]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchParams({ q: query });
    }
  };

  const pages = Math.ceil(total / limit);

  return (
    <div className="min-h-screen bg-background dark:bg-background" data-testid="ai-headnotes-page">
      <div className="bg-white dark:bg-background border-b border-muted dark:border-border">
        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-slate-900 dark:text-primary-foreground flex items-center gap-3" data-testid="ai-headnotes-title">
            <Sparkles className="text-primary" size={28} />
            AI Headnotes
          </h1>
          <p className="text-sm text-muted-foreground dark:text-muted-foreground mt-1">
            AI-generated case summaries and headnotes
          </p>
        </div>
      </div>

      <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
        <form onSubmit={handleSearch} className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-4 mb-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <Input
                placeholder="Search AI headnotes..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-10 text-base bg-background dark:bg-background"
                data-testid="ai-headnotes-input"
              />
            </div>
            <Button type="submit" className="bg-background hover:bg-card" data-testid="ai-headnotes-search-btn">
              Search
            </Button>
          </div>
          
          <div className="flex items-center gap-2 mt-3">
            <Filter size={14} className="text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Filter:</span>
            {['all', 'constitutional', 'criminal', 'civil', 'tax'].map((f) => (
              <button
                key={f}
                onClick={() => { setFilter(f); if (query.trim()) searchHeadnotes(query, 1); }}
                className={`px-2 py-0.5 rounded text-xs ${filter === f ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
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
            <p className="text-muted-foreground dark:text-muted-foreground">Searching headnotes...</p>
          </div>
        ) : results.length === 0 && query ? (
          <div className="p-12 text-center">
            <BookOpen size={48} className="text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground dark:text-muted-foreground">No headnotes found for "{query}"</p>
          </div>
        ) : (
          <>
            <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border overflow-hidden">
              <div className="p-4 border-b border-muted dark:border-border flex items-center justify-between">
                <h2 className="font-semibold text-slate-800 dark:text-primary-foreground">
                  {total.toLocaleString()} headnotes found
                </h2>
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {results.map((result, idx) => (
                  <button
                    key={idx}
                    onClick={() => navigate(`/case/${encodeURIComponent(result.case_id || result.casename)}`)}
                    className="w-full flex items-start gap-4 p-4 hover:bg-background dark:hover:bg-card/50 text-left transition-colors"
                    data-testid={`headnote-result-${idx}`}
                  >
                    <div className="w-8 h-8 rounded-lg bg-primary/10 dark:bg-primary/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Sparkles size={14} className="text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-mono text-sm text-primary mb-1">
                        {result.citation_display || result.citation || result.case_id}
                      </p>
                      <p className="text-slate-900 dark:text-primary-foreground font-medium mb-2">
                        {result.parties || result.title || 'Untitled Case'}
                      </p>
                      <div className="bg-muted/50 dark:bg-muted/20 rounded-lg p-3">
                        <p className="text-sm text-muted-foreground dark:text-muted-foreground italic">
                          {result.headnote || result.ai_headnote || 'No headnote available'}
                        </p>
                      </div>
                      <p className="text-xs text-muted-foreground dark:text-muted-foreground mt-2">
                        {result.court} {result.year && `• ${result.year}`}
                      </p>
                    </div>
                    <ChevronRight size={18} className="text-muted-foreground flex-shrink-0 mt-2" />
                  </button>
                ))}
              </div>
            </div>

            {pages > 1 && (
              <div className="mt-6 flex items-center justify-between">
                <p className="text-sm text-muted-foreground dark:text-muted-foreground">
                  Page {page} of {pages}
                </p>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => searchHeadnotes(query, page - 1)}>
                    <ChevronLeft size={16} className="mr-1" /> Previous
                  </Button>
                  <Button variant="outline" size="sm" disabled={page >= pages} onClick={() => searchHeadnotes(query, page + 1)}>
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
