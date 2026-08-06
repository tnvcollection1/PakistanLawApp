import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Loader2, Search, BookOpen, X, ArrowLeft, Scale, ChevronLeft, ChevronRight } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import SidebarLayout from '../components/SidebarLayout';
import api from '../api/api';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

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

const DictionaryPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [allEntries, setAllEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalEntries, setTotalEntries] = useState(0);
  const [grandTotal, setGrandTotal] = useState(0);
  const [selectedLetter, setSelectedLetter] = useState(searchParams.get('letter') || 'A');
  const [searchKeyword, setSearchKeyword] = useState(searchParams.get('q') || '');
  
  const [selectedWord, setSelectedWord] = useState(searchParams.get('word') || null);
  const [selectedMeaning, setSelectedMeaning] = useState('');
  const [cases, setCases] = useState([]);
  const [casesLoading, setCasesLoading] = useState(false);
  const [casesTotal, setCasesTotal] = useState(0);
  const [casesPage, setCasesPage] = useState(1);
  const casesLimit = 20;

  useEffect(() => { if (!selectedWord) fetchEntries(); }, [selectedLetter]);
  useEffect(() => { if (selectedWord) fetchCasesForWord(selectedWord); }, [selectedWord, casesPage]);

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const params = { limit: 500 };
      if (selectedLetter) params.letter = selectedLetter;
      const response = await api.pls.getDictionary(params);
      setAllEntries(response.data || []);
      setTotalEntries(response.total || 0);
      if (response.grand_total) setGrandTotal(response.grand_total);
    } catch (e) {
      setAllEntries([]);
    } finally { setLoading(false); }
  };

  const fetchCasesForWord = async (word) => {
    setCasesLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/search/caselaws?q=${encodeURIComponent(word)}&page=${casesPage}&limit=${casesLimit}&search_content=true`);
      const data = await response.json();
      setCases(data.data || []);
      setCasesTotal(data.total || 0);
    } catch (e) { setCases([]); }
    finally { setCasesLoading(false); }
  };

  const filteredEntries = useMemo(() => {
    if (!searchKeyword.trim()) return allEntries;
    const keyword = searchKeyword.toLowerCase();
    return allEntries.filter(entry => 
      (entry.word && entry.word.toLowerCase().includes(keyword)) ||
      (entry.meaning && entry.meaning.toLowerCase().includes(keyword))
    );
  }, [allEntries, searchKeyword]);

  const handleLetterClick = (letter) => {
    setSelectedLetter(letter);
    setSearchParams({ letter });
    setSearchKeyword('');
    setSelectedWord(null);
  };

  const handleWordClick = (word, meaning) => {
    setSelectedWord(word);
    setSelectedMeaning(meaning);
    setCasesPage(1);
    setSearchParams({ word });
  };

  const handleBack = () => {
    setSelectedWord(null);
    setSelectedMeaning('');
    setCases([]);
    setCasesTotal(0);
    setCasesPage(1);
    setSearchParams({ letter: selectedLetter });
  };

  const totalCasesPages = Math.ceil(casesTotal / casesLimit);

  if (selectedWord) {
    return (
      <SidebarLayout>
        <div className="min-h-screen bg-background" data-testid="dictionary-cases-page">
          <div className="bg-white dark:bg-card border-b border-border">
            <div className="max-w-screen-2xl mx-auto px-6 py-4">
              <Button variant="ghost" onClick={handleBack} className="mb-3 text-muted-foreground hover:text-foreground">
                <ArrowLeft size={16} className="mr-2" /> Back to Dictionary
              </Button>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                <BookOpen className="text-primary" size={28} /> {selectedWord}
              </h1>
              {selectedMeaning && (
                <p className="text-sm text-muted-foreground mt-2 max-w-3xl leading-relaxed bg-muted/30 p-3 rounded-lg">
                  <span className="font-medium">Definition:</span> {selectedMeaning}
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
                <div className="p-12 text-center"><Loader2 size={32} className="animate-spin text-primary mx-auto mb-3" /><p className="text-muted-foreground">Loading cases...</p></div>
              ) : cases.length === 0 ? (
                <div className="p-12 text-center"><Scale size={48} className="text-muted-foreground mx-auto mb-3" /><p className="text-muted-foreground">No cases found for "{selectedWord}"</p></div>
              ) : (
                <>
                  <div className="px-5 py-3 bg-muted/30 border-b border-border flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Showing {((casesPage - 1) * casesLimit) + 1} - {Math.min(casesPage * casesLimit, casesTotal)} of {casesTotal.toLocaleString()} cases</span>
                    <span className="text-sm text-muted-foreground">Page {casesPage} of {totalCasesPages}</span>
                  </div>
                  <div className="divide-y divide-border">
                    {cases.map((c, idx) => (
                      <div key={idx} onClick={() => navigate(`/case/${c.case_id || c._id}`)} className="p-5 hover:bg-accent/40 cursor-pointer transition-colors" data-testid={`case-result-${idx}`}>
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1"><span className="font-semibold text-primary">{c.citation || c.case_id}</span>{c.year && <span className="text-xs px-2 py-0.5 bg-muted rounded text-muted-foreground">{c.year}</span>}</div>
                            <p className="text-sm font-medium text-foreground mb-1">{c.parties || `${c.petitioner || ''} vs ${c.respondent || ''}`}</p>
                            <p className="text-xs text-muted-foreground">{c.court} {c.judge && `| Judge: ${c.judge}`}</p>
                            {c.snippet_highlighted ? (
                              <div className="mt-2 text-xs text-muted-foreground bg-muted/30 rounded px-3 py-2 border-l-2 border-primary/40">
                                <span className="block text-[10px] uppercase tracking-wider text-muted-foreground/70 mb-1">Found in judgment:</span>
                                <p className="line-clamp-2 [&>mark]:bg-yellow-200 [&>mark]:dark:bg-yellow-900/50 [&>mark]:px-0.5 [&>mark]:rounded" dangerouslySetInnerHTML={{ __html: c.snippet_highlighted }} />
                              </div>
                            ) : c.headnotes_text && (
                              <p className="mt-2 text-xs text-muted-foreground line-clamp-2">{c.headnotes_text.substring(0, 200)}...</p>
                            )}
                          </div>
                          {c.match_count > 0 && <span className="text-[10px] px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full font-medium whitespace-nowrap">{c.match_count} matches</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                  {totalCasesPages > 1 && (
                    <div className="px-5 py-4 bg-muted/30 border-t border-border flex items-center justify-center gap-2">
                      <Button variant="outline" size="sm" onClick={() => setCasesPage(p => Math.max(1, p - 1))} disabled={casesPage === 1}><ChevronLeft size={16} /> Previous</Button>
                      <span className="text-sm text-muted-foreground px-4">Page {casesPage} of {totalCasesPages}</span>
                      <Button variant="outline" size="sm" onClick={() => setCasesPage(p => Math.min(totalCasesPages, p + 1))} disabled={casesPage === totalCasesPages}>Next <ChevronRight size={16} /></Button>
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

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background" data-testid="dictionary-page">
        <div className="bg-white dark:bg-card border-b border-border">
          <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-foreground flex items-center gap-3"><BookOpen className="text-primary" size={24} /> Legal Dictionary</h1>
            <p className="text-sm text-muted-foreground mt-2">{grandTotal > 0 ? grandTotal.toLocaleString() : totalEntries.toLocaleString()} legal terms {selectedLetter && totalEntries > 0 ? `• ${totalEntries.toLocaleString()} starting with "${selectedLetter}"` : ''} • Click any term to view related cases</p>
          </div>
        </div>
        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-8">
          <div className="bg-white dark:bg-card rounded-xl border border-border p-4 mb-6">
            <div className="flex flex-wrap gap-1.5 justify-center">
              {ALPHABET.map((letter) => (
                <button key={letter} onClick={() => handleLetterClick(letter)} className={`w-9 h-9 rounded-lg text-sm font-semibold transition-all ${selectedLetter === letter ? 'bg-primary text-primary-foreground shadow-md' : 'bg-muted text-foreground hover:bg-primary/10'}`} data-testid={`letter-${letter}`}>{letter}</button>
              ))}
            </div>
          </div>
          <div className="bg-white dark:bg-card rounded-xl border border-border p-4 mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <Input placeholder="Filter entries..." value={searchKeyword} onChange={(e) => setSearchKeyword(e.target.value)} className="pl-10 pr-10" data-testid="dictionary-search" />
              {searchKeyword && <button onClick={() => setSearchKeyword('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"><X size={18} /></button>}
            </div>
            <p className="text-sm text-muted-foreground mt-2">Showing {filteredEntries.length} entries for letter "{selectedLetter}"{searchKeyword && ` matching "${searchKeyword}"`}</p>
          </div>
          <div className="bg-white dark:bg-card rounded-xl border border-border overflow-hidden">
            {loading ? (
              <div className="p-12 text-center"><Loader2 size={32} className="animate-spin text-primary mx-auto mb-3" /><p className="text-muted-foreground">Loading...</p></div>
            ) : filteredEntries.length === 0 ? (
              <div className="p-16 text-center"><BookOpen size={48} className="text-muted-foreground mx-auto mb-4" /><p className="text-muted-foreground font-medium">No entries found</p><p className="text-muted-foreground text-sm mt-1">Try a different letter or search term</p></div>
            ) : (
              <div className="divide-y divide-border">
                {filteredEntries.map((entry, idx) => (
                  <div key={idx} className="p-5 hover:bg-accent/40 transition-colors cursor-pointer group" data-testid={`entry-${idx}`} onClick={() => handleWordClick(entry.word, entry.meaning || entry.definition)}>
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="font-semibold text-primary text-base mb-2 group-hover:underline"><HighlightText text={entry.word} highlight={searchKeyword} /></h3>
                        <p className="text-sm text-muted-foreground leading-relaxed line-clamp-2"><HighlightText text={entry.meaning || entry.definition || 'No definition available'} highlight={searchKeyword} /></p>
                      </div>
                      <div className="flex items-center gap-2 text-muted-foreground group-hover:text-primary flex-shrink-0"><Scale size={14} /><span className="text-xs">View Cases</span></div>
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

export default DictionaryPage;
