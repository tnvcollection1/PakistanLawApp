import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  BarChart3, BookOpen, Scale, Gavel, Users, TrendingUp,
  Search, Clock, Star, ChevronRight
} from "lucide-react";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function DashboardModern() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [recentCases, setRecentCases] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      const [statsRes, casesRes] = await Promise.all([
        api.get("/stats").catch(() => ({ data: null })),
        api.get("/cases/recent").catch(() => ({ data: [] }))
      ]);
      setStats(statsRes.data);
      setRecentCases(casesRes.data || []);
    } catch (err) {
      setStats(null);
      setRecentCases([]);
    } finally {
      setIsLoading(false);
    }
  };

  const quickActions = [
    { label: "Search Cases", icon: Search, path: "/search", color: "bg-blue-500/20 text-blue-400" },
    { label: "Browse Statutes", icon: BookOpen, path: "/statutes", color: "bg-green-500/20 text-green-400" },
    { label: "Judge Search", icon: Gavel, path: "/judges", color: "bg-amber-500/20 text-amber-400" },
    { label: "Lawyer Search", icon: Users, path: "/lawyers", color: "bg-purple-500/20 text-purple-400" },
  ];

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Dashboard" onMenuClick={() => setSidebarOpen(true)} />

        <div className="p-6 overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {/* Welcome */}
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-white">Welcome to Pakistan Legal Scales</h1>
              <p className="text-slate-400 mt-1">Your comprehensive legal research platform</p>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {quickActions.map((action, i) => (
                <motion.button
                  key={action.label}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  onClick={() => navigate(action.path)}
                  className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4 text-left hover:bg-slate-800/60 transition-colors"
                >
                  <div className={`w-10 h-10 rounded-lg ${action.color} flex items-center justify-center mb-3`}>
                    <action.icon className="w-5 h-5" />
                  </div>
                  <span className="text-white font-medium text-sm">{action.label}</span>
                </motion.button>
              ))}
            </div>

            {/* Stats */}
            {isLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="h-24 rounded-xl bg-slate-800/40 animate-pulse" />
                ))}
              </div>
            ) : stats ? (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <BookOpen className="w-4 h-4 text-blue-400" />
                    <span className="text-slate-400 text-sm">Total Cases</span>
                  </div>
                  <div className="text-2xl font-bold text-white">{stats.total_cases?.toLocaleString() ?? 0}</div>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.1 }}
                  className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Scale className="w-4 h-4 text-green-400" />
                    <span className="text-slate-400 text-sm">Statutes</span>
                  </div>
                  <div className="text-2xl font-bold text-white">{stats.total_statutes?.toLocaleString() ?? 0}</div>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Gavel className="w-4 h-4 text-amber-400" />
                    <span className="text-slate-400 text-sm">Judges</span>
                  </div>
                  <div className="text-2xl font-bold text-white">{stats.total_judges?.toLocaleString() ?? 0}</div>
                </motion.div>
              </div>
            ) : null}

            {/* Recent Cases */}
            <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-semibold flex items-center gap-2">
                  <Clock className="w-4 h-4 text-slate-400" /> Recently Added Cases
                </h3>
                <button
                  onClick={() => navigate("/search")}
                  className="text-sm text-sky-400 hover:text-sky-300 flex items-center gap-1"
                >
                  View All <ChevronRight className="w-4 h-4" />
                </button>
              </div>
              
              {recentCases.length === 0 ? (
                <p className="text-slate-400 text-sm">No recent cases to display.</p>
              ) : (
                <div className="space-y-3">
                  {recentCases.map((c, idx) => (
                    <motion.div
                      key={c.id || idx}
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-700/30 transition-colors cursor-pointer"
                      onClick={() => navigate(`/case/${c.id}`)}
                    >
                      <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0">
                        <BookOpen className="w-4 h-4 text-blue-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-white text-sm truncate">{c.title || c.citation}</p>
                        <p className="text-slate-400 text-xs">{c.court} {c.year && `• ${c.year}`}</p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-500 shrink-0" />
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
