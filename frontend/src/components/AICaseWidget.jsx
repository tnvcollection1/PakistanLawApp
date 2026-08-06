import React, { useState, useEffect } from 'react';
import { Sparkles, Wand2, BookOpen, MessageSquare, ArrowRight, Loader } from 'lucide-react';

export default function AICaseWidget({ caseId, caseData }) {
  const [activeFeature, setActiveFeature] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState('');

  const features = [
    { id: 'summary', label: 'Generate Summary', icon: BookOpen, prompt: 'case-summary' },
    { id: 'headnotes', label: 'Generate Headnotes', icon: Wand2, prompt: 'generate-headnotes' },
    { id: 'related', label: 'Find Related Cases', icon: Sparkles, prompt: 'find-related' },
    { id: 'ask', label: 'Ask Question', icon: MessageSquare, prompt: 'ask-about-case' },
  ];

  const runAI = async (featureId) => {
    if (loading) return;
    setLoading(true);
    setActiveFeature(featureId);
    setResult(null);

    try {
      const feature = features.find(f => f.id === featureId);
      const endpoint = `/api/ai/${feature.prompt}`;

      const body = { case_id: caseId };
      if (featureId === 'ask') {
        if (!question.trim()) {
          setLoading(false);
          return;
        }
        body.question = question;
      }
      if (featureId === 'summary') {
        body.style = 'brief';
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      setResult(data);
    } catch (e) {
      setResult({ error: true, message: 'AI service is temporarily unavailable. Please try again later.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border p-4 mb-4">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles size={18} className="text-[#c9a227]" />
        <h3 className="font-semibold text-[#1a365d]">AI Assistant</h3>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-4">
        {features.map((feature) => {
          const Icon = feature.icon;
          const isActive = activeFeature === feature.id;
          return (
            <button
              key={feature.id}
              onClick={() => runAI(feature.id)}
              disabled={loading}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors
                ${isActive ? 'bg-[#1a365d] text-white' : 'bg-gray-50 hover:bg-gray-100'}`}
            >
              <Icon size={14} />
              {feature.label}
            </button>
          );
        })}
      </div>

      {activeFeature === 'ask' && (
        <div className="mb-3">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about this case..."
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#1a365d]"
            onKeyDown={(e) => e.key === 'Enter' && runAI('ask')}
          />
        </div>
      )}

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Loader size={14} className="animate-spin" />
          Generating AI response...
        </div>
      )}

      {result && !loading && (
        <div className="bg-gray-50 rounded-lg p-3 text-sm">
          {result.error ? (
            <p className="text-red-600">{result.message}</p>
          ) : (
            <div>
              {result.summary && <p className="leading-relaxed">{result.summary}</p>}
              {result.headnotes && <p className="leading-relaxed">{result.headnotes}</p>}
              {result.related_cases && result.related_cases.length > 0 && (
                <div>
                  <p className="font-medium mb-2">Related Cases:</p>
                  <div className="space-y-1">
                    {result.related_cases.map((rc, i) => (
                      <a key={i} href={`/cases/${rc.id}`} className="block text-[#1a365d] hover:underline">
                        {rc.citation || rc.title}
                      </a>
                    ))}
                  </div>
                </div>
              )}
              {result.answer && <p className="leading-relaxed">{result.answer}</p>}
              {result.explanation && <p className="leading-relaxed">{result.explanation}</p>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
