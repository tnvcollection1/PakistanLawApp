import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Network, Search, Loader2, ChevronRight, AlertCircle, BookOpen, ArrowRight } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

export default function CitationNetworkPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [network, setNetwork] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const searchNetwork = async (q) => {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/case/network?citation=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setNetwork(data);
    } catch (e) {
      setError(e.message);
      setNetwork(null);
    }
    setLoading(false);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    searchNetwork(query);
  };

  return (
    <div className="min-h-screen bg-background dark:bg-background" data-testid="citation-network-page">
      <div className="bg-white dark:bg-background border-b border-muted dark:border-border">
        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-slate-900 dark:text-primary-foreground flex items-center gap-3" data-testid="citation-network-title">
            <Network className="text-primary" size={28} />
            Citation Network
          </h1>
          <p className="text-sm text-muted-foreground dark:text-muted-foreground mt-1">
            Explore how cases cite each other
          </p>
        </div>
      </div>

      <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
        <form onSubmit={handleSearch} className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-4 mb-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <Input
                placeholder="Enter citation (e.g., 2020 SCMR 123)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-10 text-base bg-background dark:bg-background"
                data-testid="citation-network-input"
              />
            </div>
            <Button type="submit" className="bg-background hover:bg-card" data-testid="citation-network-search-btn">
              Explore
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
            <p className="text-muted-foreground dark:text-muted-foreground">Loading network...</p>
          </div>
        ) : network && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-6">
              <h2 className="font-semibold text-slate-800 dark:text-primary-foreground mb-4 flex items-center gap-2">
                <BookOpen size={18} /> Center Case
              </h2>
              <div className="p-4 bg-muted/50 dark:bg-muted/20 rounded-lg">
                <p className="font-mono text-sm text-primary">{network.citation}</p>
                <p className="text-slate-900 dark:text-primary-foreground font-medium mt-1">{network.title}</p>
                <p className="text-sm text-muted-foreground mt-1">{network.court} {network.year && `• ${network.year}`}</p>
              </div>
            </div>

            <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-6">
              <h2 className="font-semibold text-slate-800 dark:text-primary-foreground mb-4 flex items-center gap-2">
                <Network size={18} /> Cited By ({network.cited_by?.length || 0})
              </h2>
              {network.cited_by?.length > 0 ? (
                <div className="space-y-3">
                  {network.cited_by.map((c, idx) => (
                    <button
                      key={idx}
                      onClick={() => navigate(`/case/${encodeURIComponent(c.case_id || c.casename)}`)}
                      className="w-full text-left p-3 rounded-lg hover:bg-muted dark:hover:bg-muted/50 transition-colors flex items-center justify-between"
                    >
                      <div>
                        <p className="font-mono text-sm text-primary">{c.citation}</p>
                        <p className="text-slate-900 dark:text-primary-foreground">{c.title || c.parties}</p>
                      </div>
                      <ArrowRight size={16} className="text-muted-foreground" />
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No cases found citing this case</p>
              )}
            </div>

            <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-6">
              <h2 className="font-semibold text-slate-800 dark:text-primary-foreground mb-4 flex items-center gap-2">
                <BookOpen size={18} /> Cites ({network.cites?.length || 0})
              </h2>
              {network.cites?.length > 0 ? (
                <div className="space-y-3">
                  {network.cites.map((c, idx) => (
                    <button
                      key={idx}
                      onClick={() => navigate(`/case/${encodeURIComponent(c.case_id || c.casename)}`)}
                      className="w-full text-left p-3 rounded-lg hover:bg-muted dark:hover:bg-muted/50 transition-colors flex items-center justify-between"
                    >
                      <div>
                        <p className="font-mono text-sm text-primary">{c.citation}</p>
                        <p className="text-slate-900 dark:text-primary-foreground">{c.title || c.parties}</p>
                      </div>
                      <ArrowRight size={16} className="text-muted-foreground" />
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No cited cases found</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
