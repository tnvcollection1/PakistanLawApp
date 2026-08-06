import React, { useState } from "react";
import { Search, X } from "lucide-react";

const API = process.env.REACT_APP_API_URL || "/api";

export default function CaseSearchBox({ caseId }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/case/${caseId}/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      setResults(data);
    } catch (e) {
      setResults({ total: 0, snippets: [], error: true });
    }
    setLoading(false);
  };

  return (
    <div className="bg-white rounded-xl border p-4 mb-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder="Search within this case..."
          className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#1a365d]"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="bg-[#1a365d] text-white px-4 py-2 rounded-lg text-sm hover:bg-[#234e8e] disabled:opacity-50"
        >
          {loading ? "..." : <Search size={16} />}
        </button>
        {results && (
          <button onClick={() => { setResults(null); setQuery(""); }} className="p-2 hover:bg-gray-100 rounded-lg">
            <X size={16} />
          </button>
        )}
      </div>
      {results && (
        <div className="mt-3">
          <p className="text-xs text-gray-500 mb-2">{results.total} matches found</p>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {results.snippets?.map((s, i) => (
              <div key={i} className="text-xs bg-gray-50 p-2 rounded border-l-2 border-[#c9a227]">
                <span dangerouslySetInnerHTML={{ __html: s.highlighted.replace(/\*\*/g, "<mark>") }} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
