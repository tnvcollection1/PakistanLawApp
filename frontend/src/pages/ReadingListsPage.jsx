import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { List, ChevronLeft, Plus, Trash2, BookOpen, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function ReadingListsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [lists, setLists] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newListName, setNewListName] = useState("");
  const [showForm, setShowForm] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchLists();
  }, []);

  const fetchLists = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/reading-lists");
      setLists(res.data || []);
    } catch (err) {
      setLists([]);
    } finally {
      setIsLoading(false);
    }
  };

  const createList = async () => {
    if (!newListName.trim()) {
      toast({ title: "List name is required", variant: "destructive" });
      return;
    }
    try {
      const res = await api.post("/reading-lists", { name: newListName });
      setLists(prev => [res.data, ...prev]);
      setNewListName("");
      setShowForm(false);
      toast({ title: "Reading list created" });
    } catch (err) {
      toast({ title: "Failed to create list", variant: "destructive" });
    }
  };

  const deleteList = async (id) => {
    if (!window.confirm("Delete this reading list?")) return;
    try {
      await api.delete(`/reading-lists/${id}`);
      setLists(prev => prev.filter(l => l.id !== id));
      toast({ title: "List deleted" });
    } catch (err) {
      toast({ title: "Failed to delete list", variant: "destructive" });
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Reading Lists" onMenuClick={() => setSidebarOpen(true)} />

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
                  <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                    <List className="w-5 h-5 text-indigo-400" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-white">Reading Lists</h1>
                    <p className="text-slate-400 text-sm">Organize cases into collections</p>
                  </div>
                </div>
              </div>
              <Button
                className="bg-indigo-600 hover:bg-indigo-700"
                onClick={() => setShowForm(!showForm)}
              >
                <Plus className="w-4 h-4 mr-1" /> New List
              </Button>
            </div>

            {showForm && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4 mb-4"
              >
                <Input
                  placeholder="List name"
                  className="bg-slate-800 border-slate-700 text-white mb-3"
                  value={newListName}
                  onChange={(e) => setNewListName(e.target.value)}
                />
                <div className="flex gap-2">
                  <Button className="bg-indigo-600" onClick={createList}>
                    Create
                  </Button>
                  <Button variant="outline" onClick={() => setShowForm(false)}>
                    Cancel
                  </Button>
                </div>
              </motion.div>
            )}

            {isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="h-24 rounded-xl bg-slate-800/40 animate-pulse" />
                ))}
              </div>
            ) : lists.length === 0 ? (
              <div className="text-center py-20 text-slate-400">
                <List className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>No reading lists yet.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {lists.map((list, idx) => (
                  <motion.div
                    key={list.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4 hover:bg-slate-800/60 transition-colors cursor-pointer group"
                    onClick={() => navigate(`/reading-list/${list.id}`)}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                          <BookOpen className="w-5 h-5 text-indigo-400" />
                        </div>
                        <div>
                          <h3 className="text-white font-medium">{list.name}</h3>
                          <p className="text-slate-400 text-sm">{list.case_count || 0} cases</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-slate-400 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={(e) => { e.stopPropagation(); deleteList(list.id); }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                        <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 transition-colors" />
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
