import React, { useState } from 'react';
import { FileText, BookOpen, Briefcase, ArrowRight, Loader } from 'lucide-react';

export default function AISummaryPanel({ caseId }) {
  const [style, setStyle] = useState('brief');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  const styles = [
    { id: 'brief', label: 'Brief', icon: FileText, description: '3-4 sentences, key holding' },
    { id: 'detailed', label: 'Detailed', icon: BookOpen, description: 'Full facts, issues, analysis' },
    { id: 'bench', label: 'Bench Style', icon: Briefcase, description: 'For judges, ratio decidendi' },
  ];

  const generateSummary = async () => {
    if (loading) return;
    setLoading(true);
    setSummary(null);

    try {
      const res = await fetch('/api/ai/case-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_id: caseId, style }),
      });

      const data = await res.json();
      setSummary(data.summary || 'No summary generated.');
    } catch (e) {
      setSummary('AI service is temporarily unavailable. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border p-4">
      <h3 className="font-semibold text-[#1a365d] mb-3">AI Case Summary</h3>

      <div className="grid grid-cols-3 gap-2 mb-4">
        {styles.map((s) => {
          const Icon = s.icon;
          return (
            <button
              key={s.id}
              onClick={() => setStyle(s.id)}
              className={`flex flex-col items-center gap-1 p-3 rounded-lg border text-sm transition-colors
                ${style === s.id ? 'border-[#1a365d] bg-[#1a365d] text-white' : 'border-gray-200 hover:bg-gray-50'}`}
            >
              <Icon size={18} />
              <span className="font-medium">{s.label}</span>
              <span className="text-xs opacity-75">{s.description}</span>
            </button>
          );
        })}
      </div>

      <button
        onClick={generateSummary}
        disabled={loading}
        className="w-full bg-[#1a365d] text-white py-2 rounded-lg hover:bg-[#234e8e] disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {loading ? <><Loader size={16} className="animate-spin" /> Generating...</> : <><ArrowRight size={16} /> Generate Summary</>}
      </button>

      {summary && (
        <div className="mt-4 bg-gray-50 rounded-lg p-3 text-sm leading-relaxed">
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}
