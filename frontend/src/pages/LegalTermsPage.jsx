import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Loader2, Search, Library, X, ArrowLeft, Scale, ChevronLeft, ChevronRight } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import SidebarLayout from '../components/SidebarLayout';
import api from '../api/api';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

const LegalTermsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [allEntries, setAllEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalEntries, setTotalEntries] = useState(0);
  const [grandTotal, setGrandTotal] = useState(0);
  const [selectedLetter, setSelectedLetter] = useState(searchParams.get('letter') || 'A');
  const [searchKeyword, setSearchKeyword] = useState('');
  
  // Selected term and cases
  const [selectedTerm, setSelectedTerm] = useState(searchParams.get('term') || null);
  const [cases, setCases] = useState([]);
  const [casesLoading, setCasesLoading] = useState(false);
  const [casesTotal, setCasesTotal] = useState(0);
  const [casesPage, setCasesPage] = useState(1);
  const casesLimit = 20;

  useEffect(() => {
    if (!selectedTerm) {
      fetchEntries();
    }
  }, [selectedLetter]);

  useEffect(() => {
    api.pls.getStats().then(s => setGrandTotal(s.legal_terms || 0)).catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedTerm) {
      fetchCasesForTerm(selectedTerm);
    }
  }, [selectedTerm, casesPage]);

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const params = { limit: 500 };
      if (selectedLetter) params.letter = selectedLetter;
      const response = await api.pls.getLegalTerms(params);
      setAllEntries(response.data || []);
      setTotalEntries(response.total || 0);
    } catch (e) {
      console.error('Error fetching legal terms:', e);
      setAllEntries([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchCasesForTerm = async (term) => {
    setCasesLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/api/search/caselaws?q=${encodeURIComponent(term)}&page=${casesPage}&limit=${casesLimit}&search_content=true`
      );
      const data = await response.json();
      setCases(data.data || []);
      setCasesTotal(data.total || 0);
    } catch (e) {
      console.error('Error fetching cases:', e);
      setCases([]);
    } finally {
      setCasesLoading(false);
    }
  };

  const filteredEntries = useMemo(() => {
    if (!searchKeyword.trim()) return allEntries;
    const keyword = searchKeyword.toLowerCase();
    return allEntries.filter(entry => 
      (entry.term && entry.term.toLowerCase().includes(keyword))
    );
  }, [allEntries, searchKeyword]);

  const handleLetterClick = (letter) => {
    setSelectedLetter(letter);
    setSearchParams({ letter });
    setSearchKeyword('');
    setSelectedTerm(null);
  };

  const handleTermClick = (term) => {
    setSelectedTerm(term);
    setCasesPage(1);
    setSearchParams({ term });
  };

  const handleBack = () => {
    setSelectedTerm(null);
    setCases([]);
    setCasesTotal(0);
    setCasesPage(1);
    setSearchParams({ letter: selectedLetter });
  };

  const totalCasesPages = Math.ceil(casesTotal / casesLimit);

  // Show cases for selected term
  if (selectedTerm) {
    return (
      <SidebarLayout>
        <div className="min-h-screen bg-background" data-testid="legal-terms-cases-page">
          {/* Header */}
          <div className="bg-white dark:bg-card border-b border-border">
            <div className="max-w-screen-2xl mx-auto px-6 py-4">
              <Button 
                variant="ghost" 
                onClick={handleBack}
                className="mb-3 text-muted-foreground hover:text-foreground"
              >
                <ArrowLeft size={16} className="mr-2" />
                Back to Legal Terms
              </Button>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                <Library className="text-primary" size={28} />
                {selectedTerm}
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Found <span className="font-semibold text-primary">{casesTotal.toLocaleString()}</span> cases containing this term
              </p>
            </div>
          </div>

          {/* Cases List */}
          <div className="max-w-screen-2xl mx-auto px-6 py-6">
            <div className="bg-white dark:bg-card rounded-xl border border-border overflow-hidden">
              {casesLoading ? (
                <div className="p-12 text-center">
                  <Loader2 size={32} className="animate-spin text-primary mx-auto mb-3" />
                  <p className="text-muted-foreground">Loading cases...</p>
                </div>
              ) : cases.length === 0 ? (
                <div className="p-12 text-center">
                  <Scale size={48} className="text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground">No cases found for "{selectedTerm}"</p>
                </div>
              ) : (
                <>
                  {/* Results header */}
                  <div className="px-5 py-3 bg-muted/30 border-b border-border flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      Showing {((casesPage - 1) * casesLimit) + 1} - {Math.min(casesPage * casesLimit, casesTotal)} of {casesTotal.toLocaleString()} cases
                    </span>
                    <span className="text-sm text-muted-foreground">
                      Page {casesPage} of {totalCasesPages}
                    </span>
                  </div>

                  {/* Cases */}
                  <div className="divide-y divide-border">
                    {cases.map((caseItem, idx) => (
                      <div 
                        key={idx}
                        onClick={() => navigate(`/case/${caseItem.case_id || caseItem._id}`)}
                        className="p-5 hover:bg-accent/40 cursor-pointer transition-colors"
                        data-testid={`case-result-${idx}`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-primary">{caseItem.citation || caseItem.case_id}</span>
                              {caseItem.year && (
                                <span className="text-xs px-2 py-0.5 bg-muted rounded text-muted-foreground">{caseItem.year}</span>
                              )}
                            </div>
                            <p className="text-sm font-medium text-foreground mb-1">
                              {caseItem.parties || `${caseItem.petitioner || ''} vs ${caseItem.respondent || ''}`}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {caseItem.court} {caseItem.judge && `| Judge: ${caseItem.judge}`}
                            </p>
                            {caseItem.snippet_highlighted ? (
                              <div className="mt-2 text-xs text-muted-foreground bg-muted/30 rounded px-3 py-2 border-l-2 border-primary/40">
                                <span className="block text-[10px] uppercase tracking-wider text-muted-foreground/70 mb-1">Found in judgment:</span>
                                <p 
                                  className="line-clamp-2 [&>mark]:bg-yellow-200 [&>mark]:dark:bg-yellow-900/50 [&>mark]:px-0.5 [&>mark]:rounded"
                                  dangerouslySetInnerHTML={{ __html: caseItem.snippet_highlighted }}
                                />
                              </div>
                            ) : caseItem.headnotes_text && (
                              <p className="mt-2 text-xs text-muted-foreground line-clamp-2">
                                {caseItem.headnotes_text.substring(0, 200)}...
                              </p>
                            )}
                          </div>
                          {caseItem.match_count > 0 && (
                            <span className="text-[10px] px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full font-medium whitespace-nowrap">
                              {caseItem.match_count} matches
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Pagination */}
                  {totalCasesPages > 1 && (
                    <div className="px-5 py-4 bg-muted/30 border-t border-border flex items-center justify-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCasesPage(p => Math.max(1, p - 1))}
                        disabled={casesPage === 1}
                      >
                        <ChevronLeft size={16} />
                        Previous
                      </Button>
                      <span className="text-sm text-muted-foreground px-4">
                        Page {casesPage} of {totalCasesPages}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCasesPage(p => Math.min(totalCasesPages, p + 1))}
                        disabled={casesPage === totalCasesPages}
                      >
                        Next
                        <ChevronRight size={16} />
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

  // Show list of legal terms
  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background" data-testid="legal-terms-page">
        <div className="bg-white dark:bg-card border-b border-border">
          <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-foreground flex items-center gap-3">
              <Library className="text-primary" size={28} />
              Legal Terms
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              {grandTotal > 0 ? grandTotal.toLocaleString() : totalEntries.toLocaleString()} legal terms and phrases {selectedLetter && totalEntries > 0 ? `• ${totalEntries.toLocaleString()} starting with "${selectedLetter}"` : ''} • Click any term to view related cases
            </p>
          </div>
        </div>

        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
          {/* Alphabet */}
          <div className="bg-white dark:bg-card rounded-xl border border-border p-4 mb-6">
            <div className="flex flex-wrap gap-1 justify-center">
              {ALPHABET.map((letter) => (
                <button
                  key={letter}
                  onClick={() => handleLetterClick(letter)}
                  className={`w-9 h-9 rounded-lg text-sm font-medium transition-all ${
                    selectedLetter === letter
                      ? 'bg-primary text-primary-foreground shadow-md'
                      : 'bg-muted text-foreground hover:bg-primary/10'
                  }`}
                >
                  {letter}
                </button>
              ))}
            </div>
          </div>

          {/* Search */}
          <div className="bg-white dark:bg-card rounded-xl border border-border p-4 mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <Input
                placeholder="Filter terms..."
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                className="pl-10 pr-10"
              />
              {searchKeyword && (
                <button onClick={() => setSearchKeyword('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  <X size={18} />
                </button>
              )}
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Showing {filteredEntries.length} terms for letter "{selectedLetter}"
            </p>
          </div>

          {/* List */}
          <div className="bg-white dark:bg-card rounded-xl border border-border overflow-hidden">
            {loading ? (
              <div className="p-12 text-center">
                <Loader2 size={32} className="animate-spin text-primary mx-auto mb-3" />
                <p className="text-muted-foreground">Loading...</p>
              </div>
            ) : filteredEntries.length === 0 ? (
              <div className="p-12 text-center">
                <Library size={48} className="text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground">No terms found</p>
              </div>
            ) : (
              <div className="divide-y divide-border">
                {filteredEntries.map((entry, idx) => (
                  <div 
                    key={idx} 
                    className="p-4 hover:bg-accent/40 flex items-center justify-between cursor-pointer group transition-colors"
                    onClick={() => handleTermClick(entry.term)}
                    data-testid={`legal-term-${idx}`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-primary/10 rounded flex items-center justify-center">
                        <Library size={14} className="text-primary" />
                      </div>
                      <h3 className="font-semibold text-primary text-base group-hover:underline">{entry.term}</h3>
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground group-hover:text-primary">
                      <Scale size={14} />
                      <span className="text-xs">View Cases</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
};

export default LegalTermsPage;
