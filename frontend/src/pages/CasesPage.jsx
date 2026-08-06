import React, { useState } from 'react';

export default function CasesPage() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetch(`/api/cases?page=${page}`)
      .then(r => r.json())
      .then(data => {
        setCases(data.cases || []);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setLoading(false);
      });
  }, [page]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Case Law Database</h1>
      {loading ? (
        <div className="text-center py-8">Loading cases...</div>
      ) : (
        <div className="space-y-4">
          {cases.map((c) => (
            <div key={c.id} className="bg-white rounded-lg shadow p-4">
              <h3 className="font-bold text-lg">{c.title}</h3>
              <p className="text-sm text-gray-600">{c.court} | {c.date}</p>
              <p className="text-gray-700 mt-2">{c.headnotes?.substring(0, 200)}...</p>
            </div>
          ))}
          <div className="flex justify-center gap-2 mt-4">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border rounded-lg disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              className="px-4 py-2 border rounded-lg"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
