import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  BarChart3, Users, BookOpen, Gavel, TrendingUp, Activity,
  ChevronLeft, ArrowUpRight, ArrowDownRight, Calendar
} from "lucide-react";
import { Button } from "@/components/ui/button";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function EnterpriseDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/enterprise/stats");
      setStats(res.data);
    } catch (err) {
      setStats(null);
    } finally {
      setIsLoading(false);
    }
  };

  const statCards = [
    { label: "Total Cases", value: stats?.total_cases ?? 0, icon: BookOpen, color: "bg-blue-500/20 text-blue-400", trend: stats?.cases_trend },
    { label: "Active Users", value: stats?.active_users ?? 0, icon: Users, color: "bg-green-500/20 text-green-400", trend: stats?.users_trend },
    { label: "Judges", value: stats?.total_judges ?? 0, icon: Gavel, color: "bg-amber-500/20 text-amber-400", trend: stats?.judges_trend },
    { label: "Searches Today", value: stats?.searches_today ?? 0, icon: Activity, color: "bg-purple-500/20 text-purple-400", trend: stats?.searches_trend },
  ];

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Enterprise Dashboard" onMenuClick={() => setSidebarOpen(true)} />

        <div className="p-6 overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <div className="flex items-center gap-4 mb-6">
              <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                <ChevronLeft className="w-5 h-5 text-slate-300" />
              </Button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-indigo-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Enterprise Dashboard</h1>
                  <p className="text-slate-400 text-sm">Organizational analytics and insights</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {statCards.map((s, i) => (
                <motion.div
                  key={s.label}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className={`w-9 h-9 rounded-lg ${s.color} flex items-center justify-center`}>
                      <s.icon className="w-4 h-4" />
                    </div>
                    {s.trend !== undefined && (
                      <div className={`flex items-center gap-0.5 text-xs ${s.trend >= 0 ? "text-green-400" : "text-red-400"}`}>
                        {s.trend >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                        {Math.abs(s.trend)}%
                      </div>
                    )}
                  </div>
                  <div className="text-2xl font-bold text-white">{s.value.toLocaleString()}</div>
                  <div className="text-sm text-slate-400">{s.label}</div>
                </motion.div>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5"
              >
                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-indigo-400" /> Top Courts
                </h3>
                {stats?.top_courts?.length ? (
                  <div className="space-y-3">
                    {stats.top_courts.map((c, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <div className="w-8 text-sm text-slate-500 text-right">#{i + 1}</div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm text-slate-300">{c.name}</span>
                            <span className="text-sm text-slate-400">{c.count}</span>
                          </div>
                          <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                            <motion.div
                              className="h-full bg-indigo-500 rounded-full"
                              initial={{ width: 0 }}
                              animate={{ width: `${(c.count / (stats.top_courts[0].count || 1)) * 100}%` }}
                              transition={{ delay: 0.5 + i * 0.1, duration: 0.5 }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-400 text-sm">No court data available.</p>
                )}
              </motion.div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5"
              >
                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-indigo-400" /> Recent Activity
                </h3>
                {stats?.recent_activity?.length ? (
                  <div className="space-y-3">
                    {stats.recent_activity.map((a, i) => (
                      <div key={i} className="flex items-start gap-3 text-sm">
                        <div className="w-2 h-2 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                        <div>
                          <p className="text-slate-300">{a.description}</p>
                          <p className="text-slate-500 text-xs">{a.time}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-400 text-sm">No recent activity.</p>
                )}
              </motion.div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
