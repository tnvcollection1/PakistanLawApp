import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import SidebarLayout from '../components/SidebarLayout';
import { Search, Gavel, Loader2, ChevronRight, Users, Scale, TrendingUp } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

export default function JudgeSearchPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [judges, setJudges] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [mode, setMode] = useState('list'); // 'list' or 'search'
  const limit = 20;

  // Fetch top judges on mount
  useEffect(() => {
    fetchTopJudges();
  }, []);

  // Search when query changes in URL
  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setQuery(q);
      setMode('search');
      searchCases(q, 1);
    }
  }, [searchParams]);

  const fetchTopJudges = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/autocomplete/judges?limit=100`);
      const data = await res.json();
      setJudges(data.judges || []);
    } catch (e) {
      console.error('Error fetching judges:', e);
    }
    setLoading(false);
  };

  const filterJudges = useCallback(async (q) => {
    if (!q.trim()) {
      fetchTopJudges();
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API}/autocomplete/judges?q=${encodeURIComponent(q)}&limit=100`);
      const data = await res.json();
      setJudges(data.judges || []);
    } catch (e) {
      console.error('Error filtering judges:', e);
    }
    setLoading(false);
  }, []);

  const searchCases = async (judgeName, p = 1) => {
    setSearchLoading(true);
    setMode('search');
    try {
      const params = new URLSearchParams({ q: judgeName, page: p, limit });
      const res = await fetch(`${API}/search/judges?${params}`);
      const data = await res.json();
      setResults(data.data || []);
      setTotal(data.total || 0);
      setPage(p);
    } catch (e) {
      console.error('Error searching cases:', e);
    }
    setSearchLoading(false);
  };

  const handleJudgeClick = (judgeName) => {
    setQuery(judgeName);
    setSearchParams({ q: judgeName });
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchParams({ q: query });
    }
  };

  const backToList = () => {
    setMode('list');
    setQuery('');
    setSearchParams({});
    setResults([]);
    fetchTopJudges();
  };

  const pages = Math.ceil(total / limit);

  return (
    <SidebarLayout showSearchSidebar>
      <div className="min-h-screen bg-background dark:bg-background" data-testid="judge-search-page">
        {/* Header */}
        <div className="bg-white dark:bg-background border-b border-muted dark:border-border">
          <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-slate-900 dark:text-primary-foreground flex items-center gap-3" data-testid="judge-search-title">
              <Gavel className="text-primary" size={28} />
              Judge Search
            </h1>
            <p className="text-sm text-muted-foreground dark:text-muted-foreground mt-1">
              {mode === 'list' ? 'Browse judges or search by name' : `Cases by ${query}`}
            </p>
          </div>
        </div>

        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
          {/* Search form */}
          <form onSubmit={handleSearch} className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-4 mb-6">
            <div className="flex gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
                <Input
                  placeholder="Search judge name..."
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value);
                    if (mode === 'list') filterJudges(e.target.value);
                  }}
                  className="pl-10 text-base bg-background dark:bg-background"
                  data-testid="judge-search-input"
                />
              </div>
              <Button type="submit" className="bg-background hover:bg-card" data-testid="judge-search-btn">
                Search Cases
              </Button>
              {mode === 'search' && (
                <Button type="button" variant="outline" onClick={backToList} data-testid="back-to-list-btn">
                  Back to List
                </Button>
              )}
            </div>
          </form>

          {/* Judge List Mode */}
          {mode === 'list' && (
            <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border overflow-hidden">
              <div className="p-4 border-b border-muted dark:border-border flex items-center justify-between">
                <h2 className="font-semibold text-slate-800 dark:text-primary-foreground flex items-center gap-2">
                  <Users size={18} className="text-slate-800 dark:text-foreground" />
                  {query ? `Judges matching "${query}"` : 'Top Judges by Case Count'}
                </h2>
                {loading && <Loader2 size={18} className="animate-spin text-primary" />}
              </div>

              {loading && judges.length === 0 ? (
                <div className="p-12 text-center">
                  <Loader2 size={32} className="animate-spin text-slate-800 dark:text-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground dark:text-muted-foreground">Loading judges...</p>
                </div>
              ) : judges.length === 0 ? (
                <div className="p-12 text-center">
                  <Gavel size={48} className="text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground dark:text-muted-foreground">No judges found</p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {judges.map((judge, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleJudgeClick(judge.name)}
                      className="w-full flex items-center gap-4 p-4 hover:bg-background dark:hover:bg-card/50 text-left transition-colors"
                      data-testid={`judge-item-${idx}`}
                    >
                      <div className="w-10 h-10 rounded-lg bg-primary/10 dark:bg-primary/30 flex items-center justify-center flex-shrink-0">
                        <Gavel size={18} className="text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-slate-900 dark:text-primary-foreground truncate">{judge.name}</p>
                        <p className="text-sm text-muted-foreground dark:text-muted-foreground flex items-center gap-1">
                          <Scale size={12} />
                          {judge.case_count?.toLocaleString()} cases
                        </p>
                      </div>
                      <ChevronRight size={18} className="text-muted-foreground flex-shrink-0" />
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Search Results Mode */}
          {mode === 'search' && (
            <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border overflow-hidden">
              <div className="p-4 border-b border-muted dark:border-border flex items-center justify-between">
                <h2 className="font-semibold text-slate-800 dark:text-primary-foreground">
                  {searchLoading ? 'Searching...' : `${total.toLocaleString()} cases found`}
                </h2>
              </div>

              {searchLoading ? (
                <div className="p-12 text-center">
                  <Loader2 size={32} className="animate-spin text-slate-800 dark:text-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground dark:text-muted-foreground">Searching cases...</p>
                </div>
              ) : results.length === 0 ? (
                <div className="p-12 text-center">
                  <Scale size={48} className="text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground dark:text-muted-foreground">No cases found for this judge</p>
                </div>
              ) : (
                <>
                  <div className="divide-y divide-slate-100 dark:divide-slate-800">
                    {results.map((caseItem, idx) => (
                      <button
                        key={idx}
                        onClick={() => navigate(`/case/${encodeURIComponent(caseItem.case_id || caseItem.casename)}`)}
                        className="w-full flex items-center gap-4 p-4 hover:bg-background dark:hover:bg-card/50 text-left transition-colors"
                        data-testid={`case-result-${idx}`}
                      >
                        <div className="flex-1 min-w-0">
                          <p className="font-mono text-sm text-primary mb-1">
                            {caseItem.citation_display || caseItem.citation || caseItem.case_id}
                          </p>
                          <p className="text-slate-900 dark:text-primary-foreground truncate">
                            {caseItem.parties || caseItem.title || 'Untitled Case'}
                          </p>
                          <p className="text-sm text-muted-foreground dark:text-muted-foreground mt-1">
                            {caseItem.court} {caseItem.year && `• ${caseItem.year}`}
                          </p>
                        </div>
                        <ChevronRight size={18} className="text-muted-foreground flex-shrink-0" />
                      </button>
                    ))}
                  </div>

                  {/* Pagination */}
                  {pages > 1 && (
                    <div className="p-4 border-t border-muted dark:border-border flex items-center justify-between">
                      <p className="text-sm text-muted-foreground dark:text-muted-foreground">
                        Page {page} of {pages}
                      </p>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={page <= 1}
                          onClick={() => searchCases(query, page - 1)}
                        >
                          Previous
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={page >= pages}
                          onClick={() => searchCases(query, page + 1)}
                        >
                          Next
                        </Button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </SidebarLayout>
  );
}
