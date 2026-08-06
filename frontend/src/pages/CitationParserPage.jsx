import React, { useState } from 'react';

export default function CitationParserPage() {
  const [citation, setCitation] = useState('');
  const [parsed, setParsed] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleParse = async () => {
    if (!citation.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/citation-parser', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ citation })
      });
      const data = await res.json();
      setParsed(data);
    } catch (e) {
      console.error('Parse error:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Citation Parser</h1>
      <p className="text-gray-600 mb-4">Enter a legal citation to parse and find the referenced case.</p>
      
      <div className="flex gap-2 mb-6">
        <input
          type="text"
          value={citation}
          onChange={(e) => setCitation(e.target.value)}
          placeholder="e.g., 2023 SCMR 1234"
          className="flex-1 px-4 py-2 border rounded-lg"
        />
        <button
          onClick={handleParse}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Parsing...' : 'Parse'}
        </button>
      </div>

      {parsed && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-2">Parsed Citation</h2>
          <pre className="bg-gray-100 p-4 rounded-lg overflow-auto">{JSON.stringify(parsed, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
