import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BarChart, LineChart, PieChart, TrendingUp, BookOpen, Scale, Users, Gavel, Search } from 'lucide-react';
import { getAnalytics, getPopularSections, getCases } from '../api/api';

export default function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [popularSections, setPopularSections] = useState([]);
  const [recentCases, setRecentCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [analyticsData, sectionsData, casesData] = await Promise.all([
          getAnalytics(),
          getPopularSections(10),
          getCases(1, 5),
        ]);
        setAnalytics(analyticsData);
        setPopularSections(sectionsData.sections || []);
        setRecentCases(casesData.data || []);
      } catch (e) {
        console.error('Failed to load dashboard data:', e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1a365d]"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-[#1a365d] mb-8">Analytics Dashboard</h1>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Cases</p>
              <p className="text-2xl font-bold text-[#1a365d]">{analytics?.total_cases?.toLocaleString() || '369,810+'}</p>
            </div>
            <BookOpen className="h-8 w-8 text-[#c9a227]" />
          </div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Courts</p>
              <p className="text-2xl font-bold text-[#1a365d]">{analytics?.total_courts || '329'}</p>
            </div>
            <Scale className="h-8 w-8 text-[#c9a227]" />
          </div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Judges</p>
              <p className="text-2xl font-bold text-[#1a365d]">{analytics?.total_judges?.toLocaleString() || '62,424'}</p>
            </div>
            <Users className="h-8 w-8 text-[#c9a227]" />
          </div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Years Covered</p>
              <p className="text-2xl font-bold text-[#1a365d]">1950 - 2024</p>
            </div>
            <TrendingUp className="h-8 w-8 text-[#c9a227]" />
          </div>
        </div>
      </div>

      {/* Popular Sections */}
      <div className="bg-white rounded-xl p-6 shadow-sm border mb-8">
        <h2 className="text-xl font-bold text-[#1a365d] mb-4 flex items-center gap-2">
          <Gavel size={20} />
          Popular Legal Sections
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {popularSections.map((section) => (
            <div key={`${section.act}-${section.section}`} className="bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition">
              <p className="font-semibold text-[#1a365d]">Section {section.section}</p>
              <p className="text-xs text-gray-500">{section.act}</p>
              <p className="text-xs text-gray-600 mt-1">{section.description}</p>
              <p className="text-xs text-[#c9a227] mt-1">{section.count?.toLocaleString()} cases</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Cases */}
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <h2 className="text-xl font-bold text-[#1a365d] mb-4 flex items-center gap-2">
          <Search size={20} />
          Recent Cases
        </h2>
        <div className="space-y-4">
          {recentCases.map((case_) => (
            <div key={case_.id} className="border-b last:border-0 pb-4 last:pb-0">
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
    </div>
  );
}
