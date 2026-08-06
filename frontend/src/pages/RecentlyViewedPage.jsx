import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Clock, ChevronLeft, BookOpen, Trash2, Eye, Scale } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function RecentlyViewedPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/history");
      setHistory(res.data || []);
    } catch (err) {
      setHistory([]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearHistory = async () => {
    if (!window.confirm("Clear all recently viewed cases?")) return;
    try {
      await api.delete("/history");
      setHistory([]);
      toast({ title: "History cleared" });
    } catch (err) {
      toast({ title: "Failed to clear history", variant: "destructive" });
    }
  };

  const removeItem = async (id) => {
    try {
      await api.delete(`/history/${id}`);
      setHistory(prev => prev.filter(h => h.id !== id));
    } catch (err) {
      toast({ title: "Failed to remove item", variant: "destructive" });
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Recently Viewed" onMenuClick={() => setSidebarOpen(true)} />

        <div className="p-6 overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                  <ChevronLeft className="w-5 h-5 text-slate-300" />
                </Button>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-sky-500/20 flex items-center justify-center">
                    <Clock className="w-5 h-5 text-sky-400" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-white">Recently Viewed</h1>
                    <p className="text-slate-400 text-sm">Your case viewing history</p>
                  </div>
                </div>
              </div>
              {history.length > 0 && (
                <Button variant="outline" size="sm" onClick={clearHistory} className="border-red-800/50 text-red-400 hover:bg-red-900/20">
                  <Trash2 className="w-4 h-4 mr-1" /> Clear All
                </Button>
              )}
            </div>
          </motion.div>

          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-20 rounded-xl bg-slate-800/40 animate-pulse" />
              ))}
            </div>
          ) : history.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-20 text-slate-400"
            >
              <Clock className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <h3 className="text-lg font-medium text-white mb-2">No history yet</h3>
              <p>Cases you view will appear here.</p>
            </motion.div>
          ) : (
            <div className="space-y-3">
              {history.map((item, idx) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4 flex items-center gap-4 hover:bg-slate-800/60 transition-colors group"
                >
                  <div className="w-10 h-10 rounded-lg bg-sky-500/20 flex items-center justify-center shrink-0">
                    <BookOpen className="w-5 h-5 text-sky-400" />
                  </div>
                  <div
                    className="flex-1 min-w-0 cursor-pointer"
                    onClick={() => navigate(`/case/${item.case_id}`)}
                  >
                    <h3 className="text-white font-medium truncate group-hover:text-sky-300 transition-colors">
                      {item.title}
                    </h3>
                    <div className="flex items-center gap-3 mt-1 text-sm text-slate-400">
                      <span className="flex items-center gap-1"><Scale className="w-3 h-3" /> {item.court}</span>
                      <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> {item.viewed_at}</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" className="text-slate-400 hover:text-red-400 shrink-0"
                    onClick={() => removeItem(item.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
