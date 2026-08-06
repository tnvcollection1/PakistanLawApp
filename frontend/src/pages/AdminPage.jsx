import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Users, BookOpen, TrendingUp, Activity, Settings } from 'lucide-react';

export default function AdminPage() {
  const [stats, setStats] = useState({ cases: 0, users: 0, searches: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const res = await fetch('/api/analytics/overview');
        const data = await res.json();
        setStats({ cases: data.total_cases || 0, users: data.total_users || 0, searches: data.total_searches || 0 });
      } catch (e) {
        console.error('Failed to load stats:', e);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-[#1a365d] mb-8">Admin Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Cases</p>
              <p className="text-2xl font-bold text-[#1a365d]">{stats.cases.toLocaleString()}</p>
            </div>
            <BookOpen className="h-8 w-8 text-[#c9a227]" />
          </div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Users</p>
              <p className="text-2xl font-bold text-[#1a365d]">{stats.users.toLocaleString()}</p>
            </div>
            <Users className="h-8 w-8 text-[#c9a227]" />
          </div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Searches</p>
              <p className="text-2xl font-bold text-[#1a365d]">{stats.searches.toLocaleString()}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-[#c9a227]" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-xl font-bold text-[#1a365d] mb-4">Management</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link to="/admin/users" className="flex items-center gap-3 p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition">
            <Users size={20} className="text-[#1a365d]" />
            <span className="font-medium">Manage Users</span>
          </Link>
          <Link to="/admin/cases" className="flex items-center gap-3 p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition">
            <BookOpen size={20} className="text-[#1a365d]" />
            <span className="font-medium">Manage Cases</span>
          </Link>
          <Link to="/admin/analytics" className="flex items-center gap-3 p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition">
            <Activity size={20} className="text-[#1a365d]" />
            <span className="font-medium">Analytics</span>
          </Link>
          <Link to="/admin/settings" className="flex items-center gap-3 p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition">
            <Settings size={20} className="text-[#1a365d]" />
            <span className="font-medium">Settings</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
