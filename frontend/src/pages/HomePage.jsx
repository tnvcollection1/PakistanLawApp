import React, { useState, useEffect } from 'react';

export default function HomePage() {
  const [stats, setStats] = useState({ cases: 0, statutes: 0, citations: 0 });

  useEffect(() => {
    fetch('/api/stats')
      .then(r => r.json())
      .then(data => setStats(data))
      .catch(console.error);
  }, []);

  return (
    <div className="space-y-8">
      <section className="text-center py-12 bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-xl">
        <h1 className="text-4xl font-bold mb-4">Pakistan Law Research Platform</h1>
        <p className="text-xl opacity-90">Search case law, statutes, and legal precedents</p>
      </section>

      <section className="grid grid-cols-3 gap-4">
        <div className="p-6 bg-white rounded-lg shadow text-center">
          <div className="text-3xl font-bold text-blue-600">{stats.cases.toLocaleString()}</div>
          <div className="text-gray-600">Cases</div>
        </div>
        <div className="p-6 bg-white rounded-lg shadow text-center">
          <div className="text-3xl font-bold text-blue-600">{stats.statutes.toLocaleString()}</div>
          <div className="text-gray-600">Statutes</div>
        </div>
        <div className="p-6 bg-white rounded-lg shadow text-center">
          <div className="text-3xl font-bold text-blue-600">{stats.citations.toLocaleString()}</div>
          <div className="text-gray-600">Citations</div>
        </div>
      </section>

      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Recent Updates</h2>
        <p className="text-gray-600">Latest case law and statutory updates will appear here.</p>
      </section>
    </div>
  );
}
