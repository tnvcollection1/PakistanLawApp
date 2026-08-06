import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Bell, ChevronLeft, AlertTriangle, Info, CheckCircle, Trash2, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

const typeIcons = {
  alert: AlertTriangle,
  info: Info,
  update: CheckCircle,
};

const typeColors = {
  alert: "bg-red-500/20 text-red-400",
  info: "bg-blue-500/20 text-blue-400",
  update: "bg-green-500/20 text-green-400",
};

export default function AlertsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterType, setFilterType] = useState("all");
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/alerts");
      setAlerts(res.data || []);
    } catch (err) {
      setAlerts([]);
    } finally {
      setIsLoading(false);
    }
  };

  const markAsRead = async (id) => {
    try {
      await api.patch(`/alerts/${id}/read`);
      setAlerts(prev => prev.map(a => a.id === id ? { ...a, read: true } : a));
    } catch (err) {
      toast({ title: "Failed to mark as read", variant: "destructive" });
    }
  };

  const deleteAlert = async (id) => {
    try {
      await api.delete(`/alerts/${id}`);
      setAlerts(prev => prev.filter(a => a.id !== id));
      toast({ title: "Alert deleted" });
    } catch (err) {
      toast({ title: "Failed to delete alert", variant: "destructive" });
    }
  };

  const filtered = alerts.filter(a => filterType === "all" || a.type === filterType);
  const unreadCount = alerts.filter(a => !a.read).length;

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Alerts" onMenuClick={() => setSidebarOpen(true)} />

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
                  <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
                    <Bell className="w-5 h-5 text-red-400" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-white">Alerts</h1>
                    <p className="text-slate-400 text-sm">
                      {unreadCount > 0 ? `${unreadCount} unread` : "No new alerts"}
                    </p>
                  </div>
                </div>
              </div>
              <select
                className="px-3 py-2 rounded-md bg-slate-800/60 border border-slate-700 text-white text-sm"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <option value="all">All Alerts</option>
                <option value="alert">Alerts</option>
                <option value="info">Info</option>
                <option value="update">Updates</option>
              </select>
            </div>

            {isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="h-20 rounded-xl bg-slate-800/40 animate-pulse" />
                ))}
              </div>
            ) : filtered.length === 0 ? (
              <div className="text-center py-20 text-slate-400">
                <Bell className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>No alerts found.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {filtered.map((alert, idx) => {
                  const Icon = typeIcons[alert.type] || Info;
                  return (
                    <motion.div
                      key={alert.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className={`rounded-xl border p-4 flex items-start gap-4 transition-colors ${
                        alert.read
                          ? "border-slate-700/50 bg-slate-800/20"
                          : "border-slate-700/50 bg-slate-800/40"
                      }`}
                    >
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${typeColors[alert.type] || typeColors.info}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h3 className="text-white font-medium">{alert.title}</h3>
                          {!alert.read && (
                            <span className="w-2 h-2 rounded-full bg-red-400" />
                          )}
                        </div>
                        <p className="text-slate-400 text-sm mt-1">{alert.message}</p>
                        <p className="text-slate-500 text-xs mt-1">{alert.created_at}</p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {!alert.read && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-sky-400 hover:text-sky-300"
                            onClick={() => markAsRead(alert.id)}
                          >
                            Mark Read
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-slate-400 hover:text-red-400"
                          onClick={() => deleteAlert(alert.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
