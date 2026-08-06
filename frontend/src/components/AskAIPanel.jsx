import React, { useState } from 'react';
import { Bot, X, Loader2, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import MarkdownCitation from './MarkdownCitation';

const API = process.env.REACT_APP_BACKEND_URL || '';

const AskAIPanel = ({ caseId, caseTitle }) => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);

  const analyzeCase = async () => {
    setOpen(true);
    if (analysis) return; // Already loaded
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/api/chatbot/analyze-case`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_id: caseId }),
      });
      if (!res.ok) throw new Error('Failed to analyze');
      const data = await res.json();
      setAnalysis(data.analysis);
    } catch (e) {
      setError('Failed to generate analysis. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    return (
      <Button
        onClick={analyzeCase}
        className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md"
        data-testid="ask-ai-btn"
      >
        <Sparkles size={16} className="mr-2" /> Ask AI About This Case
      </Button>
    );
  }

  return (
    <Card className="border-indigo-200 shadow-lg" data-testid="ai-analysis-panel">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Bot size={20} className="text-slate-800 dark:text-slate-200" />
          AI Case Analysis
        </CardTitle>
        <Button variant="ghost" size="sm" onClick={() => setOpen(false)}>
          <X size={16} />
        </Button>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-slate-800 dark:text-slate-200 mb-3" />
            <p className="text-sm text-slate-500 dark:text-muted-foreground">Analyzing case with AI...</p>
            <p className="text-xs text-muted-foreground mt-1">This may take 15-30 seconds</p>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-red-500 text-sm mb-3">{error}</p>
            <Button variant="outline" size="sm" onClick={() => { setAnalysis(null); analyzeCase(); }}>
              Try Again
            </Button>
          </div>
        ) : analysis ? (
          <div className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed max-h-[500px] overflow-y-auto">
            <MarkdownCitation content={analysis} />
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
};

export default AskAIPanel;
