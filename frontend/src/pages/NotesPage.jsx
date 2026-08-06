import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { StickyNote, ChevronLeft, Plus, Trash2, Edit2, Save, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function NotesPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notes, setNotes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newNote, setNewNote] = useState({ title: "", content: "" });
  const [editingNote, setEditingNote] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/notes");
      setNotes(res.data || []);
    } catch (err) {
      setNotes([]);
    } finally {
      setIsLoading(false);
    }
  };

  const addNote = async () => {
    if (!newNote.title.trim()) {
      toast({ title: "Title is required", variant: "destructive" });
      return;
    }
    try {
      const res = await api.post("/notes", newNote);
      setNotes(prev => [res.data, ...prev]);
      setNewNote({ title: "", content: "" });
      setShowForm(false);
      toast({ title: "Note added" });
    } catch (err) {
      toast({ title: "Failed to add note", variant: "destructive" });
    }
  };

  const updateNote = async () => {
    if (!editingNote || !editingNote.title.trim()) return;
    try {
      await api.patch(`/notes/${editingNote.id}`, editingNote);
      setNotes(prev => prev.map(n => n.id === editingNote.id ? editingNote : n));
      setEditingNote(null);
      toast({ title: "Note updated" });
    } catch (err) {
      toast({ title: "Failed to update note", variant: "destructive" });
    }
  };

  const deleteNote = async (id) => {
    if (!window.confirm("Delete this note?")) return;
    try {
      await api.delete(`/notes/${id}`);
      setNotes(prev => prev.filter(n => n.id !== id));
      toast({ title: "Note deleted" });
    } catch (err) {
      toast({ title: "Failed to delete note", variant: "destructive" });
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Notes" onMenuClick={() => setSidebarOpen(true)} />

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
                  <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                    <StickyNote className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-white">Notes</h1>
                    <p className="text-slate-400 text-sm">Your personal case notes</p>
                  </div>
                </div>
              </div>
              <Button
                className="bg-amber-600 hover:bg-amber-700"
                onClick={() => { setShowForm(!showForm); setEditingNote(null); }}
              >
                {showForm ? <X className="w-4 h-4 mr-1" /> : <Plus className="w-4 h-4 mr-1" />}
                {showForm ? "Cancel" : "Add Note"}
              </Button>
            </div>

            {showForm && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4 mb-4"
              >
                <Input
                  placeholder="Note title"
                  className="bg-slate-800 border-slate-700 text-white mb-3"
                  value={newNote.title}
                  onChange={(e) => setNewNote({ ...newNote, title: e.target.value })}
                />
                <textarea
                  placeholder="Note content..."
                  className="w-full h-24 px-3 py-2 rounded-md bg-slate-800 border border-slate-700 text-white text-sm resize-none mb-3"
                  value={newNote.content}
                  onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
                />
                <Button className="bg-amber-600 hover:bg-amber-700" onClick={addNote}>
                  <Save className="w-4 h-4 mr-1" /> Save Note
                </Button>
              </motion.div>
            )}

            {isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="h-24 rounded-xl bg-slate-800/40 animate-pulse" />
                ))}
              </div>
            ) : notes.length === 0 ? (
              <div className="text-center py-20 text-slate-400">
                <StickyNote className="w-12 h-12 mx-auto mb-4 opacity-30" />
                <p>No notes yet.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {notes.map((note, idx) => (
                  <motion.div
                    key={note.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4 hover:bg-slate-800/60 transition-colors"
                  >
                    {editingNote?.id === note.id ? (
                      <>
                        <Input
                          className="bg-slate-800 border-slate-700 text-white mb-2"
                          value={editingNote.title}
                          onChange={(e) => setEditingNote({ ...editingNote, title: e.target.value })}
                        />
                        <textarea
                          className="w-full h-20 px-3 py-2 rounded-md bg-slate-800 border border-slate-700 text-white text-sm resize-none mb-2"
                          value={editingNote.content}
                          onChange={(e) => setEditingNote({ ...editingNote, content: e.target.value })}
                        />
                        <div className="flex gap-2">
                          <Button size="sm" className="bg-amber-600" onClick={updateNote}>
                            <Save className="w-3 h-3 mr-1" /> Save
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => setEditingNote(null)}>
                            <X className="w-3 h-3 mr-1" /> Cancel
                          </Button>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="text-white font-medium">{note.title}</h3>
                          <div className="flex gap-1">
                            <Button variant="ghost" size="icon" className="text-slate-400 hover:text-amber-400"
                              onClick={() => setEditingNote(note)}
                            >
                              <Edit2 className="w-3 h-3" />
                            </Button>
                            <Button variant="ghost" size="icon" className="text-slate-400 hover:text-red-400"
                              onClick={() => deleteNote(note.id)}
                            >
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                        <p className="text-slate-400 text-sm line-clamp-3">{note.content}</p>
                        <p className="text-slate-500 text-xs mt-2">{note.updated_at}</p>
                      </>
                    )}
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
