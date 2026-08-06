import React, { useState } from 'react';

export default function SidebarLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen">
      <aside className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-gray-900 text-white transition-all duration-300 overflow-hidden`}>
        <div className="p-4">
          <h2 className="text-xl font-bold mb-4">Pakistan Law App</h2>
          <nav className="space-y-2">
            <a href="/" className="block p-2 rounded hover:bg-gray-800">Home</a>
            <a href="/cases" className="block p-2 rounded hover:bg-gray-800">Cases</a>
            <a href="/statutes" className="block p-2 rounded hover:bg-gray-800">Statutes</a>
            <a href="/citation-parser" className="block p-2 rounded hover:bg-gray-800">Citation Parser</a>
            <a href="/analytics" className="block p-2 rounded hover:bg-gray-800">Analytics</a>
          </nav>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <header className="bg-white shadow-sm p-4 flex items-center">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 mr-4"
          >
            ☰
          </button>
          <h1 className="text-xl font-semibold">Pakistan LawSite Clone</h1>
        </header>
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  );
}
