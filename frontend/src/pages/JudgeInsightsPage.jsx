import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Gavel, Scale, TrendingUp, BarChart3, Calendar, ArrowLeft,
  Loader2, AlertCircle, BookOpen
} from 'lucide-react';
import { Button } from '../components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

export default function JudgeInsightsPage() {
  const { judgeName } = useParams();
  const navigate = useNavigate();
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (judgeName) {
      fetchInsights(judgeName);
    }
  }, [judgeName]);

  const fetchInsights = async (name) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/judge/insights/${encodeURIComponent(name)}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setInsights(data);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background dark:bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 size={40} className="animate-spin text-primary mx-auto mb-3" />
          <p className="text-muted-foreground">Loading judge insights...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background dark:bg-background flex items-center justify-center">
        <div className="text-center">
          <AlertCircle size={40} className="text-red-500 mx-auto mb-3" />
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <Button variant="outline" className="mt-4" onClick={() => navigate('/judges')}>
            Back to Judges
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background dark:bg-background" data-testid="judge-insights-page">
      <div className="bg-white dark:bg-background border-b border-muted dark:border-border">
        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
          <Button variant="ghost" onClick={() => navigate('/judges')} className="mb-4">
            <ArrowLeft size={18} className="mr-2" /> Back to Judges
          </Button>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-slate-900 dark:text-primary-foreground flex items-center gap-3">
            <Gavel className="text-primary" size={28} />
            {decodeURIComponent(judgeName || '')}
          </h1>
          <p className="text-sm text-muted-foreground dark:text-muted-foreground mt-1">
            Judge insights and analytics
          </p>
        </div>
      </div>

      <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
        {insights && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-6">
                <h2 className="font-semibold text-slate-800 dark:text-primary-foreground mb-4 flex items-center gap-2">
                  <Scale size={18} /> Case Statistics
                </h2>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Cases</p>
                    <p className="text-2xl font-bold text-slate-900 dark:text-primary-foreground">
                      {insights.total_cases?.toLocaleString() || 0}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Decided</p>
                    <p className="text-xl font-semibold text-green-600">
                      {insights.decided?.toLocaleString() || 0}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Pending</p>
                    <p className="text-xl font-semibold text-amber-600">
                      {insights.pending?.toLocaleString() || 0}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-6">
                <h2 className="font-semibold text-slate-800 dark:text-primary-foreground mb-4 flex items-center gap-2">
                  <Calendar size={18} /> Court History
                </h2>
                <div className="space-y-3">
                  {insights.courts?.map((court, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">{court.name}</span>
                      <span className="text-sm font-medium">{court.years}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-6">
                <h2 className="font-semibold text-slate-800 dark:text-primary-foreground mb-4 flex items-center gap-2">
                  <TrendingUp size={18} /> Trending Topics
                </h2>
                <div className="flex flex-wrap gap-2">
                  {insights.topics?.map((topic, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 rounded-full bg-primary/10 dark:bg-primary/20 text-primary text-sm"
                    >
                      {topic}
                    </span>
                  )) || <p className="text-muted-foreground">No topic data available</p>}
                </div>
              </div>

              <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-6">
                <h2 className="font-semibold text-slate-800 dark:text-primary-foreground mb-4 flex items-center gap-2">
                  <BookOpen size={18} /> Recent Cases
                </h2>
                <div className="space-y-3">
                  {insights.recent_cases?.map((c, idx) => (
                    <button
                      key={idx}
                      onClick={() => navigate(`/case/${encodeURIComponent(c.case_id || c.casename)}`)}
                      className="w-full text-left p-3 rounded-lg hover:bg-muted dark:hover:bg-muted/50 transition-colors"
                    >
                      <p className="font-mono text-sm text-primary">{c.citation}</p>
                      <p className="text-slate-900 dark:text-primary-foreground">{c.title || c.parties}</p>
                      <p className="text-xs text-muted-foreground">{c.date}</p>
                    </button>
                  )) || <p className="text-muted-foreground">No recent cases</p>}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
