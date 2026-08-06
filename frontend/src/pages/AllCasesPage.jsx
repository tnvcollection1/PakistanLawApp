import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import { getCases } from '../api/api';

export default function AllCasesPage() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const limit = 20;

  useEffect(() => {
    async function loadCases() {
      setLoading(true);
      try {
        const data = await getCases(page, limit);
        setCases(data.data || []);
        setTotal(data.total || 0);
      } catch (e) {
        console.error('Failed to load cases:', e);
      } finally {
        setLoading(false);
      }
    }
    loadCases();
  }, [page]);

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-[#1a365d] mb-6 flex items-center gap-2">
        <BookOpen size={28} />
        All Cases
      </h1>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1a365d]"></div>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-4 border-b flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Showing {cases.length} of {total.toLocaleString()} cases
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50"
                >
                  <ChevronLeft size={16} />
                </button>
                <span className="text-sm font-medium">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>

            <div className="divide-y">
              {cases.map((case_) => (
                <div key={case_.id} className="p-4 hover:bg-gray-50 transition">
                  <Link to={`/cases/${case_.id}`} className="text-lg font-semibold text-[#1a365d] hover:underline">
                    {case_.citation || case_.title}
                  </Link>
                  <p className="text-sm text-gray-500 mt-1">
                    {case_.court} • {case_.year} • {case_.judges}
                  </p>
                  {case_.headnotes && (
                    <p className="text-sm text-gray-600 mt-2 line-clamp-2">{case_.headnotes}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-center mt-6 gap-2">
            <button
              onClick={() => setPage(1)}
              disabled={page === 1}
              className="px-3 py-1 rounded-lg border hover:bg-gray-50 disabled:opacity-50 text-sm"
            >
              First
            </button>
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronLeft size={16} />
            </button>
            <span className="px-4 py-1 text-sm font-medium">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronRight size={16} />
            </button>
            <button
              onClick={() => setPage(totalPages)}
              disabled={page >= totalPages}
              className="px-3 py-1 rounded-lg border hover:bg-gray-50 disabled:opacity-50 text-sm"
            >
              Last
            </button>
          </div>
        </>
      )}
    </div>
  );
}
