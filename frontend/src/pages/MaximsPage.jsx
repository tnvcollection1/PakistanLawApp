import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Scale, ChevronLeft, BookOpen, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function MaximsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [maxims, setMaxims] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchMaxims();
  }, []);

  const fetchMaxims = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/maxims");
      setMaxims(res.data || []);
    } catch (err) {
      setMaxims([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Legal Maxims" onMenuClick={() => setSidebarOpen(true)} />

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
                <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                  <Scale className="w-5 h-5 text-amber-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Legal Maxims</h1>
                  <p className="text-slate-400 text-sm">Time-tested principles of law</p>
                </div>
              </div>
            </div>
          </motion.div>

          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-24 rounded-xl bg-slate-800/40 animate-pulse" />
              ))}
            </div>
          ) : maxims.length === 0 ? (
            <div className="text-center py-20 text-slate-400">
              <Scale className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>No maxims found.</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {maxims.map((maxim, idx) => (
                <motion.div
                  key={maxim.id || idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5 hover:bg-slate-800/60 transition-colors"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center shrink-0">
                      <BookOpen className="w-5 h-5 text-amber-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-white font-semibold text-lg italic">{maxim.latin || maxim.maxim}</h3>
                      {maxim.meaning && (
                        <p className="text-slate-400 text-sm mt-2">{maxim.meaning}</p>
                      )}
                      {maxim.application && (
                        <p className="text-slate-500 text-sm mt-1">{maxim.application}</p>
                      )}
                    </div>
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
