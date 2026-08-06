import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Loader2, Search, FileText, X, Calendar, User, ArrowLeft, Scale, ChevronLeft, ChevronRight } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import SidebarLayout from '../components/SidebarLayout';
import api from '../api/api';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const ArticlesPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const limit = 20;

  // Selected article and cases
  const [selectedArticle, setSelectedArticle] = useState(searchParams.get('article') || null);
  const [cases, setCases] = useState([]);
  const [casesLoading, setCasesLoading] = useState(false);
  const [casesTotal, setCasesTotal] = useState(0);
  const [casesPage, setCasesPage] = useState(1);
  const casesLimit = 20;

  useEffect(() => {
    if (!selectedArticle) {
      fetchArticles();
    }
  }, [page]);

  useEffect(() => {
    if (selectedArticle) {
      fetchCasesForArticle(selectedArticle);
    }
  }, [selectedArticle, casesPage]);

  const fetchArticles = async () => {
    setLoading(true);
    try {
      const response = await api.pls.getArticles({ page, limit });
      setArticles(response.data || []);
      setTotal(response.total || 0);
    } catch (e) {
      console.error('Error fetching articles:', e);
    } finally {
      setLoading(false);
    }
  };

  const fetchCasesForArticle = async (title) => {
    setCasesLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/api/search/caselaws?q=${encodeURIComponent(title)}&page=${casesPage}&limit=${casesLimit}&search_content=true`
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

  const filteredArticles = articles.filter(a => {
    if (!searchKeyword.trim()) return true;
    const keyword = searchKeyword.toLowerCase();
    return (a.title && a.title.toLowerCase().includes(keyword)) ||
           (a.author && a.author.toLowerCase().includes(keyword));
  });

  const pages = Math.ceil(total / limit);
  const totalCasesPages = Math.ceil(casesTotal / casesLimit);

  const handleArticleClick = (title) => {
    setSelectedArticle(title);
    setCasesPage(1);
    setSearchParams({ article: title });
  };

  const handleBack = () => {
    setSelectedArticle(null);
    setCases([]);
    setCasesTotal(0);
    setCasesPage(1);
    setSearchParams({});
  };

  // Show cases for selected article
  if (selectedArticle) {
    return (
      <SidebarLayout>
        <div className="min-h-screen bg-background" data-testid="articles-cases-page">
          <div className="bg-white dark:bg-card border-b border-border">
            <div className="max-w-screen-2xl mx-auto px-6 py-4">
              <Button variant="ghost" onClick={handleBack} className="mb-3 text-muted-foreground hover:text-foreground" data-testid="back-to-articles-btn">
                <ArrowLeft size={16} className="mr-2" /> Back to Articles
              </Button>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                <FileText className="text-primary" size={28} />
                {selectedArticle}
              </h1>
              <p className="text-sm text-muted-foreground mt-2">
                Found <span className="font-semibold text-primary">{casesTotal.toLocaleString()}</span> cases related to this article
              </p>
            </div>
          </div>

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
                  <p className="text-muted-foreground">No cases found for "{selectedArticle}"</p>
                </div>
              ) : (
                <>
                  <div className="px-5 py-3 bg-muted/30 border-b border-border flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      Showing {((casesPage - 1) * casesLimit) + 1} - {Math.min(casesPage * casesLimit, casesTotal)} of {casesTotal.toLocaleString()}
                    </span>
                    <span className="text-sm text-muted-foreground">Page {casesPage} of {totalCasesPages}</span>
                  </div>
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
                              {caseItem.year && <span className="text-xs px-2 py-0.5 bg-muted rounded text-muted-foreground">{caseItem.year}</span>}
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
                                <p className="line-clamp-2 [&>mark]:bg-yellow-200 [&>mark]:dark:bg-yellow-900/50 [&>mark]:px-0.5 [&>mark]:rounded"
                                  dangerouslySetInnerHTML={{ __html: caseItem.snippet_highlighted }} />
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
                  {totalCasesPages > 1 && (
                    <div className="px-5 py-4 bg-muted/30 border-t border-border flex items-center justify-center gap-2">
                      <Button variant="outline" size="sm" onClick={() => setCasesPage(p => Math.max(1, p - 1))} disabled={casesPage === 1}>
                        <ChevronLeft size={16} /> Previous
                      </Button>
                      <span className="text-sm text-muted-foreground px-4">Page {casesPage} of {totalCasesPages}</span>
                      <Button variant="outline" size="sm" onClick={() => setCasesPage(p => Math.min(totalCasesPages, p + 1))} disabled={casesPage === totalCasesPages}>
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

  // Show articles list
  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background" data-testid="articles-page">
        <div className="bg-white dark:bg-card border-b border-border">
          <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-foreground flex items-center gap-3">
              <FileText className="text-primary" size={28} />
              Legal Articles
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              {total.toLocaleString()} articles and commentaries - Click any article to view related cases
            </p>
          </div>
        </div>

        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
          {/* Search */}
          <div className="bg-white dark:bg-card rounded-xl border border-border p-4 mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <Input
                placeholder="Search articles by title or author..."
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                className="pl-10 pr-10"
                data-testid="articles-search"
              />
              {searchKeyword && (
                <button onClick={() => setSearchKeyword('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  <X size={18} />
                </button>
              )}
            </div>
          </div>

          {/* Articles List */}
          <div className="bg-white dark:bg-card rounded-xl border border-border overflow-hidden">
            {loading ? (
              <div className="p-12 text-center">
                <Loader2 size={32} className="animate-spin text-primary mx-auto mb-3" />
                <p className="text-muted-foreground">Loading articles...</p>
              </div>
            ) : filteredArticles.length === 0 ? (
              <div className="p-12 text-center">
                <FileText size={48} className="text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground">No articles found</p>
              </div>
            ) : (
              <>
                <div className="divide-y divide-border">
                  {filteredArticles.map((article, idx) => (
                    <div
                      key={idx}
                      onClick={() => handleArticleClick(article.title || 'Untitled Article')}
                      className="p-5 hover:bg-accent/40 cursor-pointer group transition-colors"
                      data-testid={`article-${idx}`}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <h3 className="font-semibold text-primary text-base group-hover:underline mb-2">
                            {article.title || 'Untitled Article'}
                          </h3>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            {article.author && (
                              <span className="flex items-center gap-1">
                                <User size={14} />
                                {article.author}
                              </span>
                            )}
                            {article.date && (
                              <span className="flex items-center gap-1">
                                <Calendar size={14} />
                                {article.date}
                              </span>
                            )}
                            {article.journal && (
                              <span className="bg-muted px-2 py-0.5 rounded text-xs">{article.journal}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-muted-foreground group-hover:text-primary flex-shrink-0">
                          <Scale size={14} />
                          <span className="text-xs">View Cases</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {pages > 1 && (
                  <div className="px-5 py-4 bg-muted/30 border-t border-border flex items-center justify-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1}>
                      <ChevronLeft size={16} /> Previous
                    </Button>
                    <span className="text-sm text-muted-foreground px-4">Page {page} of {pages}</span>
                    <Button variant="outline" size="sm" onClick={() => setPage(p => Math.min(pages, p + 1))} disabled={page >= pages}>
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
};

export default ArticlesPage;
