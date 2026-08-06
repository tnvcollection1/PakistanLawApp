import React, { useState, useEffect } from 'react';
import { X, Download, ExternalLink, Share2, Bookmark, Loader2 } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { useAuth } from '../context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function CaseDetailModal({ caseId, onClose }) {
  const { user } = useAuth();
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [bookmarked, setBookmarked] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (caseId) fetchCase();
  }, [caseId]);

  const fetchCase = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/cases/${caseId}`);
      if (res.ok) {
        const data = await res.json();
        setCaseData(data);
        setBookmarked(data.bookmarked || false);
      } else {
        setError('Case not found');
      }
    } catch (e) {
      setError('Failed to load case');
    } finally {
      setLoading(false);
    }
  };

  const toggleBookmark = async () => {
    try {
      const res = await fetch(`${API}/api/bookmarks`, {
        method: bookmarked ? 'DELETE' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user?.username, case_id: caseId }),
      });
      if (res.ok) setBookmarked(!bookmarked);
    } catch (e) { console.error(e); }
  };

  const exportPDF = async () => {
    setExporting(true);
    try {
      window.open(`${API}/api/export/case/${caseId}/pdf`, '_blank');
    } catch (e) { console.error(e); }
    finally { setExporting(false); }
  };

  const shareCase = () => {
    const url = `${window.location.origin}/case/${caseId}`;
    navigator.clipboard.writeText(url);
    setShowShare(true);
    setTimeout(() => setShowShare(false), 2000);
  };

  if (!caseId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div className="bg-white dark:bg-card rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : error ? (
          <div className="p-8 text-center">
            <p className="text-red-500">{error}</p>
            <Button onClick={onClose} variant="outline" className="mt-4">Close</Button>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="sticky top-0 bg-white dark:bg-card border-b border-border px-6 py-4 flex items-center justify-between z-10">
              <div className="flex-1 min-w-0">
                <h2 className="text-lg font-bold text-foreground truncate">{caseData.title || caseData.citation || caseData.case_id}</h2>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="secondary" className="text-xs">{caseData.court}</Badge>
                  {caseData.year && <Badge variant="outline" className="text-xs">{caseData.year}</Badge>}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={toggleBookmark} className={`p-2 rounded-lg hover:bg-background ${bookmarked ? 'text-yellow-500' : 'text-muted-foreground'}`} title="Bookmark">
                  <Bookmark size={18} fill={bookmarked ? 'currentColor' : 'none'} />
                </button>
                <button onClick={shareCase} className="p-2 rounded-lg hover:bg-background text-muted-foreground" title="Share">
                  <Share2 size={18} />
                </button>
                <button onClick={exportPDF} disabled={exporting} className="p-2 rounded-lg hover:bg-background text-muted-foreground" title="Export PDF">
                  <Download size={18} />
                </button>
                <button onClick={onClose} className="p-2 rounded-lg hover:bg-red-50 text-red-500">
                  <X size={20} />
                </button>
              </div>
            </div>

            {showShare && (
              <div className="bg-emerald-100 text-emerald-800 px-4 py-2 text-sm text-center">Link copied to clipboard!</div>
            )}

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Metadata */}
              <div className="grid grid-cols-2 gap-4">
                {caseData.judge && (
                  <div>
                    <p className="text-xs text-muted-foreground">Judge</p>
                    <p className="text-sm font-medium">{caseData.judge}</p>
                  </div>
                )}
                {caseData.date && (
                  <div>
                    <p className="text-xs text-muted-foreground">Date</p>
                    <p className="text-sm font-medium">{caseData.date}</p>
                  </div>
                )}
                {caseData.petitioner && (
                  <div>
                    <p className="text-xs text-muted-foreground">Petitioner</p>
                    <p className="text-sm font-medium">{caseData.petitioner}</p>
                  </div>
                )}
                {caseData.respondent && (
                  <div>
                    <p className="text-xs text-muted-foreground">Respondent</p>
                    <p className="text-sm font-medium">{caseData.respondent}</p>
                  </div>
                )}
              </div>

              {/* Headnotes */}
              {caseData.headnotes && (
                <div>
                  <h3 className="text-sm font-semibold text-foreground mb-2">Headnotes</h3>
                  <div className="bg-muted/30 rounded-lg p-4 text-sm text-muted-foreground leading-relaxed">
                    {caseData.headnotes}
                  </div>
                </div>
              )}

              {/* Full Text */}
              {caseData.full_content && (
                <div>
                  <h3 className="text-sm font-semibold text-foreground mb-2">Full Judgment</h3>
                  <div className="bg-muted/30 rounded-lg p-4 text-sm leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto">
                    {caseData.full_content}
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
