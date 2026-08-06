import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Loader2, Search, BookOpen, X, ChevronLeft, ChevronRight, ArrowLeft, Scale } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import SidebarLayout from '../components/SidebarLayout';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
const CASES_PER_PAGE = 20;

const HighlightText = ({ text, highlight }) => {
  if (!highlight.trim() || !text) return <span>{text}</span>;
  const regex = new RegExp(`(${highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  const parts = String(text).split(regex);
  return (
    <span>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <mark key={i} className="bg-yellow-200 dark:bg-yellow-800 px-0.5 rounded">{part}</mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </span>
  );
};

export default function BlacksLawPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [selectedLetter, setSelectedLetter] = useState(searchParams.get('letter') || 'A');
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [page, setPage] = useState(parseInt(searchParams.get('page')) || 1);
  const [stats, setStats] = useState(null);

  // Selected term -> show related cases
  const [selectedTerm, setSelectedTerm] = useState(searchParams.get('term') || null);
  const [selectedDef, setSelectedDef] = useState('');
  const [cases, setCases] = useState([]);
  const [casesLoading, setCasesLoading] = useState(false);
  const [casesTotal, setCasesTotal] = useState(0);
  const [casesPage, setCasesPage] = useState(1);

  const fetchEntries = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page, limit: 50 });
      if (searchQuery.trim()) {
        params.set('q', searchQuery.trim());
      } else {
        params.set('letter', selectedLetter);
      }
      const res = await fetch(`${API_URL}/api/blacks-law?${params}`);
      const data = await res.json();
      setEntries(data.data || []);
      setTotal(data.total || 0);
      setTotalPages(data.pages || 0);
    } catch {
      setEntries([]);
    } finally {
      setLoading(false);
    }
  }, [selectedLetter, searchQuery, page]);

  const fetchCasesForTerm = useCallback(async (term) => {
    setCasesLoading(true);
    try {
      const res = await fetch(
        `${API_URL}/api/search/caselaws?q=${encodeURIComponent(term)}&page=${casesPage}&limit=${CASES_PER_PAGE}&search_content=true`
      );
      const data = await res.json();
      setCases(data.data || []);
      setCasesTotal(data.total || 0);
    } catch {
      setCases([]);
    } finally {
      setCasesLoading(false);
    }
  }, [casesPage]);

  useEffect(() => {
    if (!selectedTerm) fetchEntries();
  }, [fetchEntries, selectedTerm]);

  useEffect(() => {
    if (selectedTerm) fetchCasesForTerm(selectedTerm);
  }, [selectedTerm, casesPage, fetchCasesForTerm]);

  useEffect(() => {
    fetch(`${API_URL}/api/blacks-law/stats`).then(r => r.json()).then(setStats).catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedTerm) {
      setSearchParams({ term: selectedTerm }, { replace: true });
    } else {
      const params = {};
      if (searchQuery) params.q = searchQuery;
      else params.letter = selectedLetter;
      if (page > 1) params.page = page;
      setSearchParams(params, { replace: true });
    }
  }, [selectedLetter, searchQuery, page, selectedTerm, setSearchParams]);

  const handleLetterClick = (letter) => {
    setSelectedLetter(letter);
    setSearchQuery('');
    setPage(1);
  };

  const handleSearch = (val) => {
    setSearchQuery(val);
    setPage(1);
  };

  const handleTermClick = (term, definition) => {
    setSelectedTerm(term);
    setSelectedDef(definition);
    setCasesPage(1);
  };

  const handleBack = () => {
    setSelectedTerm(null);
    setSelectedDef('');
    setCases([]);
    setCasesTotal(0);
    setCasesPage(1);
  };

  const totalCasesPages = Math.ceil(casesTotal / CASES_PER_PAGE);

  // ===== CASES VIEW (when a term is clicked) =====
  if (selectedTerm) {
    return (
      <SidebarLayout>
        <div className="min-h-screen bg-background" data-testid="blacks-law-cases-view">
          <div className="bg-white dark:bg-card border-b border-border">
            <div className="max-w-screen-2xl mx-auto px-6 py-4">
              <Button
                variant="ghost"
                onClick={handleBack}
                className="mb-3 text-muted-foreground hover:text-foreground"
                data-testid="back-to-dictionary"
              >
                <ArrowLeft size={16} className="mr-2" />
                Back to Black's Law Dictionary
              </Button>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                <BookOpen className="text-primary" size={28} />
                {selectedTerm}
              </h1>
              {selectedDef && (
                <p className="text-sm text-muted-foreground mt-2 max-w-3xl leading-relaxed bg-muted/30 p-3 rounded-lg">
                  <span className="font-medium">Black's Law Dictionary:</span> {selectedDef.length > 400 ? selectedDef.slice(0, 400) + '...' : selectedDef}
                </p>
              )}
              <p className="text-sm text-muted-foreground mt-2">
                Found <span className="font-semibold text-primary">{casesTotal.toLocaleString()}</span> cases containing this term
              </p>
            </div>
          </div>

          <div className="max-w-screen-2xl mx-auto px-6 py-6">
            <div className="bg-white dark:bg-card rounded-xl border border-border overflow-hidden">
              {casesLoading ? (
                <div className="p-12 text-center">
                  <Loader2 size={32} className="animate-spin text-primary mx-auto mb-3" />
                  <p className="text-muted-foreground">Searching cases for "{selectedTerm}"...</p>
                </div>
              ) : cases.length === 0 ? (
                <div className="p-12 text-center">
                  <Scale size={48} className="text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground">No cases found for "{selectedTerm}"</p>
                </div>
              ) : (
                <>
                  <div className="px-5 py-3 bg-muted/30 border-b border-border flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      Showing {((casesPage - 1) * CASES_PER_PAGE) + 1} - {Math.min(casesPage * CASES_PER_PAGE, casesTotal)} of {casesTotal.toLocaleString()} cases
                    </span>
                    <span className="text-sm text-muted-foreground">Page {casesPage} of {totalCasesPages}</span>
                  </div>

                  <div className="divide-y divide-border">
                    {cases.map((c, idx) => (
                      <div
                        key={idx}
                        onClick={() => navigate(`/case/${c.case_id || c._id}`)}
                        className="p-5 hover:bg-accent/40 cursor-pointer transition-colors"
                        data-testid={`case-result-${idx}`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-primary">{c.citation || c.case_id}</span>
                              {c.year && <span className="text-xs px-2 py-0.5 bg-muted rounded text-muted-foreground">{c.year}</span>}
                            </div>
                            <p className="text-sm font-medium text-foreground mb-1">
                              {c.parties || `${c.petitioner || ''} vs ${c.respondent || ''}`}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {c.court} {c.judge && `| Judge: ${c.judge}`}
                            </p>
                            {c.snippet_highlighted ? (
                              <div className="mt-2 text-xs text-muted-foreground bg-muted/30 rounded px-3 py-2 border-l-2 border-primary/40">
                                <span className="block text-[10px] uppercase tracking-wider text-muted-foreground/70 mb-1">Found in judgment:</span>
                                <p
                                  className="line-clamp-2 [&>mark]:bg-yellow-200 [&>mark]:dark:bg-yellow-900/50 [&>mark]:px-0.5 [&>mark]:rounded"
                                  dangerouslySetInnerHTML={{ __html: c.snippet_highlighted }}
                                />
                              </div>
                            ) : c.headnotes_text && (
                              <p className="mt-2 text-xs text-muted-foreground line-clamp-2">
                                {c.headnotes_text.substring(0, 200)}...
                              </p>
                            )}
                          </div>
                          {c.match_count > 0 && (
                            <span className="text-[10px] px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full font-medium whitespace-nowrap">
                              {c.match_count} matches
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {totalCasesPages > 1 && (
                    <div className="px-5 py-4 bg-muted/30 border-t border-border flex items-center justify-center gap-2">
                      <Button variant="outline" size="sm" onClick={() => setCasesPage(p => Math.max(1, p - 1))} disabled={casesPage === 1}>
                        <ChevronLeft size={16} /> Previous
                      </Button>
                      <span className="text-sm text-muted-foreground px-4">Page {casesPage} of {totalCasesPages}</span>
                      <Button variant="outline" size="sm" onClick={() => setCasesPage(p => Math.min(totalCasesPages, p + 1))} disabled={casesPage >= totalCasesPages}>
                        Next <ChevronRight size={16} />
                      </Button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </SidebarLayout>
    );
  }

  // ===== DICTIONARY LISTING VIEW =====
  return (
    <SidebarLayout>
      <div className="max-w-6xl mx-auto px-4 py-6" data-testid="blacks-law-page">
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <BookOpen size={28} className="text-primary" />
            <h1 className="font-heading text-2xl md:text-3xl font-bold text-foreground">
              Black's Law Dictionary
            </h1>
          </div>
          <p className="text-sm text-muted-foreground">
            {stats ? `${stats.total.toLocaleString()} legal terms and definitions — click any term to see related cases` : 'Comprehensive legal terminology reference'}
          </p>
        </div>

        <div className="mb-4 relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search terms or definitions..."
            className="pl-10 pr-10"
            data-testid="blacks-law-search"
          />
          {searchQuery && (
            <button
              onClick={() => { setSearchQuery(''); setPage(1); }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X size={16} />
            </button>
          )}
        </div>

        {!searchQuery && (
          <div className="flex flex-wrap gap-1 mb-4" data-testid="alphabet-nav">
            {ALPHABET.map(letter => (
              <Button
                key={letter}
                variant={selectedLetter === letter ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleLetterClick(letter)}
                className="w-8 h-8 p-0 text-xs font-mono"
              >
                {letter}
              </Button>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between mb-3">
          <p className="text-sm text-muted-foreground">
            {searchQuery
              ? `${total.toLocaleString()} results for "${searchQuery}"`
              : `${total.toLocaleString()} terms starting with "${selectedLetter}"`}
          </p>
          {totalPages > 1 && (
            <p className="text-xs text-muted-foreground">Page {page} of {totalPages}</p>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="animate-spin text-primary" size={28} />
          </div>
        ) : entries.length === 0 ? (
          <div className="text-center py-16">
            <BookOpen size={48} className="text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No entries found.</p>
          </div>
        ) : (
          <div className="space-y-1">
            {entries.map((entry, idx) => (
              <div
                key={idx}
                className="border border-border rounded-sm transition-colors cursor-pointer bg-card hover:bg-primary/5 hover:border-primary/30"
                onClick={() => handleTermClick(entry.term, entry.definition)}
                data-testid={`blacks-entry-${idx}`}
              >
                <div className="px-4 py-3 flex items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-heading font-semibold text-primary text-sm">
                      <HighlightText text={entry.term} highlight={searchQuery} />
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                      <HighlightText text={entry.definition} highlight={searchQuery} />
                    </p>
                  </div>
                  <ChevronRight size={16} className="text-muted-foreground mt-1 flex-shrink-0" />
                </div>
              </div>
            ))}
          </div>
        )}

        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 mt-6 pb-6">
            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)} data-testid="prev-page">
              <ChevronLeft size={16} /> Previous
            </Button>
            <span className="text-sm text-muted-foreground px-3">{page} / {totalPages}</span>
            <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)} data-testid="next-page">
              Next <ChevronRight size={16} />
            </Button>
          </div>
        )}
      </div>
    </SidebarLayout>
  );
}
