import React, { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Calendar, ChevronLeft, Plus, Clock, CheckCircle, Circle } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";

export default function EnterpriseCalendar() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [events, setEvents] = useState([
    { id: "1", title: "Court Hearing", date: "2024-01-15", time: "10:00 AM", type: "hearing", status: "upcoming" },
    { id: "2", title: "Filing Deadline", date: "2024-01-20", time: "5:00 PM", type: "deadline", status: "upcoming" },
    { id: "3", title: "Client Meeting", date: "2024-01-18", time: "2:00 PM", type: "meeting", status: "upcoming" },
  ]);
  const navigate = useNavigate();

  const getEventIcon = (type) => {
    switch (type) {
      case "hearing": return <Clock className="w-4 h-4 text-amber-400" />;
      case "deadline": return <CheckCircle className="w-4 h-4 text-red-400" />;
      case "meeting": return <Circle className="w-4 h-4 text-green-400" />;
      default: return <Circle className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Enterprise Calendar" onMenuClick={() => setSidebarOpen(true)} />

        <div className="p-6 overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                  <ChevronLeft className="w-5 h-5 text-slate-300" />
                </Button>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                    <Calendar className="w-5 h-5 text-indigo-400" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-white">Enterprise Calendar</h1>
                    <p className="text-slate-400 text-sm">Track important dates and deadlines</p>
                  </div>
                </div>
              </div>
              <Button className="bg-indigo-600 hover:bg-indigo-700">
                <Plus className="w-4 h-4 mr-1" /> Add Event
              </Button>
            </div>

            <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
              <h3 className="text-white font-semibold mb-4">Upcoming Events</h3>
              <div className="space-y-3">
                {events.map((event, idx) => (
                  <motion.div
                    key={event.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="flex items-center gap-4 p-3 rounded-lg hover:bg-slate-700/30 transition-colors"
                  >
                    <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center">
                      {getEventIcon(event.type)}
                    </div>
                    <div className="flex-1">
                      <p className="text-white font-medium">{event.title}</p>
                      <p className="text-slate-400 text-sm">{event.date} at {event.time}</p>
                    </div>
                    <span className={`px-2 py-0.5 rounded-full text-xs ${
                      event.type === "deadline" ? "bg-red-500/20 text-red-400" :
                      event.type === "hearing" ? "bg-amber-500/20 text-amber-400" :
                      "bg-green-500/20 text-green-400"
                    }`}>
                      {event.type}
                    </span>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
