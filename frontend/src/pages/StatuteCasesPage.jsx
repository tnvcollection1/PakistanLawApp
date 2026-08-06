import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { BookOpen, Loader2, ChevronLeft, ChevronRight, Search, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import SidebarLayout from '../components/SidebarLayout';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function StatuteCasesPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const statute = searchParams.get('statute') || '';
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState(statute);

  useEffect(() => {
    if (statute) fetchCases(1);
  }, [statute]);

  const fetchCases = async (p) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/statute-cases?statute=${encodeURIComponent(statute)}&page=${p}&limit=20`);
      if (res.ok) {
        const d = await res.json();
        setData(d);
        setPage(p);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      navigate(`/statute-cases?statute=${encodeURIComponent(searchInput.trim())}`);
    }
  };

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background" data-testid="statute-cases-page">
        <div className="bg-white dark:bg-background border-b shadow-sm px-4 sm:px-6 py-4 sm:py-5">
          <div className="max-w-5xl mx-auto">
            <h1 className="text-lg sm:text-xl font-semibold text-slate-800 dark:text-foreground flex items-center gap-2" data-testid="statute-cases-title">
              <BookOpen size={20} className="text-emerald-600" /> Statute-to-Case Mapper
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground dark:text-muted-foreground mt-1">Find all cases that cite or interpret a specific statute</p>
          </div>
        </div>

        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 sm:py-8 space-y-6">
          {/* Search */}
          <Card>
            <CardContent className="p-4">
              <form onSubmit={handleSearch} className="flex gap-2">
                <div className="relative flex-1">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="text"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    placeholder="Enter statute name, e.g., Criminal Procedure Code, Contract Act 1872..."
                    className="w-full pl-10 pr-4 py-3 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    data-testid="statute-search-input"
                  />
                </div>
                <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700 px-6" data-testid="statute-search-btn">
                  Search
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Results */}
          {loading ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
          ) : data ? (
            <>
              <div className="flex items-center justify-between">
                <p className="text-sm text-foreground dark:text-muted-foreground">
                  <span className="font-semibold text-primary dark:text-primary">{data.total.toLocaleString()}</span> cases cite
                  <span className="font-medium"> "{data.statute}"</span>
                </p>
                <p className="text-sm text-muted-foreground">Page {data.page} of {data.pages}</p>
              </div>

              <div className="space-y-2">
                {data.cases.map((c) => (
                  <Card key={c.case_id} className="hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => navigate(`/case/${c.case_id}`)} data-testid={`statute-case-${c.case_id}`}>
                    <CardContent className="p-4 flex items-center justify-between">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-primary dark:text-primary text-sm">{c.case_id}</span>
                          <Badge variant="outline" className="text-xs">{c.year}</Badge>
                          <Badge variant="outline" className="text-xs">{c.court}</Badge>
                        </div>
                        <p className="text-sm text-foreground dark:text-muted-foreground truncate mt-1">{c.parties}</p>
                        {c.judge && <p className="text-xs text-muted-foreground mt-0.5">Judge: {c.judge}</p>}
                      </div>
                      <ExternalLink size={14} className="text-muted-foreground flex-shrink-0" />
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Pagination */}
              {data.pages > 1 && (
                <div className="flex justify-center gap-2 pt-4">
                  <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => fetchCases(page - 1)} data-testid="prev-page-btn">
                    <ChevronLeft size={14} /> Prev
                  </Button>
                  <span className="px-4 py-2 text-sm text-foreground dark:text-muted-foreground">Page {page} of {data.pages}</span>
                  <Button variant="outline" size="sm" disabled={page >= data.pages} onClick={() => fetchCases(page + 1)} data-testid="next-page-btn">
                    Next <ChevronRight size={14} />
                  </Button>
                </div>
              )}
            </>
          ) : !statute ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                <BookOpen size={40} className="text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium text-foreground dark:text-muted-foreground mb-2">Search for a Statute</h3>
                <p className="text-sm text-muted-foreground mb-6 max-w-md">Enter a statute name to find all cases that cite or interpret it</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {['Criminal Procedure Code', 'Contract Act', 'Constitution of Pakistan', 'Civil Procedure Code', 'Pakistan Penal Code'].map((s) => (
                    <button key={s} onClick={() => { setSearchInput(s); navigate(`/statute-cases?statute=${encodeURIComponent(s)}`); }}
                      className="px-3 py-1.5 rounded-full border text-xs text-foreground dark:text-muted-foreground hover:border-emerald-300 hover:bg-emerald-50 transition-colors"
                      data-testid={`quick-statute-${s.replace(/\s+/g, '-').toLowerCase()}`}>
                      {s}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          ) : null}
        </div>
      </div>
    </SidebarLayout>
  );
}
