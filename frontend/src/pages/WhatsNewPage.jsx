import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Zap, ChevronLeft, Clock, BookOpen, Star, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function WhatsNewPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [updates, setUpdates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUpdates();
  }, []);

  const fetchUpdates = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/updates");
      setUpdates(res.data || []);
    } catch (err) {
      setUpdates([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case "case": return <BookOpen className="w-5 h-5 text-blue-400" />;
      case "feature": return <Star className="w-5 h-5 text-amber-400" />;
      case "trending": return <TrendingUp className="w-5 h-5 text-green-400" />;
      default: return <Zap className="w-5 h-5 text-sky-400" />;
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="What's New" onMenuClick={() => setSidebarOpen(true)} />

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
                <div className="w-10 h-10 rounded-lg bg-sky-500/20 flex items-center justify-center">
                  <Zap className="w-5 h-5 text-sky-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">What's New</h1>
                  <p className="text-slate-400 text-sm">Latest updates and additions</p>
                </div>
              </div>
            </div>

            {isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="h-20 rounded-xl bg-slate-800/40 animate-pulse" />
                ))}
              </div>
            ) : updates.length === 0 ? (
              <div className="text-center py-20 text-slate-400">
                <Zap className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>No updates to display.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {updates.map((update, idx) => (
                  <motion.div
                    key={update.id || idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4 flex items-start gap-4 hover:bg-slate-800/60 transition-colors"
                  >
                    <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center shrink-0">
                      {getIcon(update.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-white font-medium">{update.title}</h3>
                      <p className="text-slate-400 text-sm mt-1">{update.description}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <Clock className="w-3 h-3 text-slate-500" />
                        <span className="text-slate-500 text-xs">{update.created_at}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
