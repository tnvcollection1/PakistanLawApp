import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Search, ChevronLeft, TrendingUp, BarChart3, Activity, ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function SearchAnalyticsDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/analytics/searches");
      setAnalytics(res.data);
    } catch (err) {
      setAnalytics(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Search Analytics" onMenuClick={() => setSidebarOpen(true)} />

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
                <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                  <Search className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Search Analytics</h1>
                  <p className="text-slate-400 text-sm">Insights into search behavior</p>
                </div>
              </div>
            </div>

            {isLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="h-24 rounded-xl bg-slate-800/40 animate-pulse" />
                ))}
              </div>
            ) : !analytics ? (
              <div className="text-center py-20 text-slate-400">
                <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>No analytics data available.</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Search className="w-4 h-4 text-purple-400" />
                      <span className="text-slate-400 text-sm">Total Searches</span>
                    </div>
                    <div className="text-2xl font-bold text-white">{analytics.total_searches?.toLocaleString() ?? 0}</div>
                  </motion.div>
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Activity className="w-4 h-4 text-green-400" />
                      <span className="text-slate-400 text-sm">Avg. Results</span>
                    </div>
                    <div className="text-2xl font-bold text-white">{analytics.avg_results?.toFixed(1) ?? 0}</div>
                  </motion.div>
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="w-4 h-4 text-blue-400" />
                      <span className="text-slate-400 text-sm">Unique Queries</span>
                    </div>
                    <div className="text-2xl font-bold text-white">{analytics.unique_queries?.toLocaleString() ?? 0}</div>
                  </motion.div>
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <ArrowUpRight className="w-4 h-4 text-amber-400" />
                      <span className="text-slate-400 text-sm">Click-Through Rate</span>
                    </div>
                    <div className="text-2xl font-bold text-white">{analytics.ctr?.toFixed(1) ?? 0}%</div>
                  </motion.div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
                    <h3 className="text-white font-semibold mb-4">Top Search Terms</h3>
                    {analytics.top_terms?.length ? (
                      <div className="space-y-3">
                        {analytics.top_terms.map((t, i) => (
                          <div key={i} className="flex items-center gap-3">
                            <div className="w-6 text-sm text-slate-500">{i + 1}</div>
                            <div className="flex-1">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm text-slate-300">{t.term}</span>
                                <span className="text-sm text-slate-400">{t.count}</span>
                              </div>
                              <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                <motion.div className="h-full bg-purple-500 rounded-full" initial={{ width: 0 }} animate={{ width: `${(t.count / (analytics.top_terms[0].count || 1)) * 100}%` }} transition={{ delay: 0.5 + i * 0.1, duration: 0.5 }} />
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-slate-400 text-sm">No search term data.</p>
                    )}
                  </motion.div>

                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
                    <h3 className="text-white font-semibold mb-4">Top Filters Used</h3>
                    {analytics.top_filters?.length ? (
                      <div className="space-y-3">
                        {analytics.top_filters.map((f, i) => (
                          <div key={i} className="flex items-center gap-3">
                            <div className="w-6 text-sm text-slate-500">{i + 1}</div>
                            <div className="flex-1">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm text-slate-300">{f.filter}</span>
                                <span className="text-sm text-slate-400">{f.count}</span>
                              </div>
                              <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                <motion.div className="h-full bg-indigo-500 rounded-full" initial={{ width: 0 }} animate={{ width: `${(f.count / (analytics.top_filters[0].count || 1)) * 100}%` }} transition={{ delay: 0.5 + i * 0.1, duration: 0.5 }} />
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-slate-400 text-sm">No filter usage data.</p>
                    )}
                  </motion.div>
                </div>
              </>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
