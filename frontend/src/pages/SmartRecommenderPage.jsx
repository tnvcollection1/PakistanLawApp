import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Sparkles, ChevronLeft, BookOpen, Scale, Gavel, ArrowRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function SmartRecommenderPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/recommendations");
      setRecommendations(res.data || []);
    } catch (err) {
      setRecommendations([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Smart Recommender" onMenuClick={() => setSidebarOpen(true)} />

        <div className="p-6 overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <div className="flex items-center gap-4 mb-4">
              <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                <ChevronLeft className="w-5 h-5 text-slate-300" />
              </Button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Smart Recommender</h1>
                  <p className="text-slate-400 text-sm">AI-powered case recommendations based on your history</p>
                </div>
              </div>
            </div>
          </motion.div>

          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
          ) : recommendations.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-20 text-slate-400"
            >
              <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <h3 className="text-lg font-medium text-white mb-2">No recommendations yet</h3>
              <p className="max-w-md mx-auto">Start searching and reading cases to get personalized recommendations.</p>
            </motion.div>
          ) : (
            <div className="grid gap-4">
              {recommendations.map((rec, idx) => (
                <motion.div
                  key={rec.id || idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5 hover:bg-slate-800/60 transition-colors cursor-pointer group"
                  onClick={() => navigate(`/case/${rec.id}`)}
                >
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center shrink-0 group-hover:bg-purple-500/30 transition-colors">
                      <BookOpen className="w-5 h-5 text-purple-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-white font-semibold text-base group-hover:text-purple-300 transition-colors truncate">
                        {rec.title}
                      </h3>
                      <div className="flex items-center gap-3 mt-1 text-sm text-slate-400 flex-wrap">
                        <span className="flex items-center gap-1"><Scale className="w-3 h-3" /> {rec.court}</span>
                        <span className="flex items-center gap-1"><Gavel className="w-3 h-3" /> {rec.date}</span>
                      </div>
                      <p className="text-slate-400 text-sm mt-2 line-clamp-2">{rec.snippet || rec.headnote}</p>
                      <div className="mt-3 flex items-center gap-2">
                        <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full">
                          {Math.round((rec.score || 0.85) * 100)}% match
                        </span>
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-purple-400 transition-colors shrink-0" />
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
