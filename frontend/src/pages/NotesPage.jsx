import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import SidebarLayout from '../components/SidebarLayout';
import { useAuth } from '../context/AuthContext';
import { FileText, Trash2, Plus, Loader2 } from 'lucide-react';
import { Textarea } from '../components/ui/textarea';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function NotesPage() {
  const { user } = useAuth();
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user?.username) fetchNotes();
  }, [user]);

  const fetchNotes = async () => {
    try {
      const res = await fetch(`${API}/api/notes?username=${user.username}`);
      if (res.ok) setNotes(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const saveNote = async (e) => {
    e.preventDefault();
    if (!title.trim() || !body.trim()) return;
    setSaving(true);
    try {
      const res = await fetch(`${API}/api/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user.username, title: title.trim(), body: body.trim() }),
      });
      if (res.ok) {
        setTitle(''); setBody(''); setShowForm(false);
        fetchNotes();
      }
    } catch (e) { console.error(e); }
    finally { setSaving(false); }
  };

  const deleteNote = async (noteId) => {
    try {
      await fetch(`${API}/api/notes/${noteId}`, { method: 'DELETE' });
      setNotes(prev => prev.filter(n => n.note_id !== noteId));
    } catch (e) { console.error(e); }
  };

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background">
        <div className="bg-white dark:bg-background border-b shadow-sm px-4 sm:px-6 py-4 sm:py-5">
          <div className="max-w-4xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h1 className="text-lg sm:text-xl font-semibold text-slate-800 dark:text-foreground flex items-center gap-2">
                <FileText size={20} className="text-slate-800 dark:text-foreground" /> My Notes
              </h1>
              <p className="text-xs sm:text-sm text-muted-foreground mt-1">Personal case law research notes</p>
            </div>
            <Button onClick={() => setShowForm(!showForm)} className="bg-background hover:bg-card w-full sm:w-auto">
              <Plus size={14} className="mr-1" /> New Note
            </Button>
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4 sm:py-8 space-y-4">
          {showForm && (
            <Card>
              <CardHeader><CardTitle className="text-lg">Create Note</CardTitle></CardHeader>
              <CardContent>
                <form onSubmit={saveNote} className="space-y-3">
                  <input
                    type="text" value={title} onChange={e => setTitle(e.target.value)}
                    placeholder="Note title..."
                    className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <Textarea value={body} onChange={e => setBody(e.target.value)} placeholder="Write your note here..." rows={6} />
                  <div className="flex gap-2">
                    <Button type="submit" disabled={saving} className="bg-background hover:bg-card">
                      {saving ? <Loader2 size={14} className="animate-spin mr-1" /> : <FileText size={14} className="mr-1" />}
                      Save Note
                    </Button>
                    <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {loading ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
          ) : notes.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                <FileText size={40} className="text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">No notes yet</h3>
                <p className="text-sm text-muted-foreground mb-4">Create your first research note</p>
                <Button onClick={() => setShowForm(true)} className="bg-background hover:bg-card">
                  <Plus size={14} className="mr-1" /> Create Note
                </Button>
              </CardContent>
            </Card>
          ) : (
            notes.map(note => (
              <Card key={note.note_id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-foreground truncate">{note.title}</h3>
                      <p className="text-sm text-muted-foreground mt-1 whitespace-pre-wrap">{note.body}</p>
                      <p className="text-xs text-muted-foreground mt-2">{new Date(note.created_at).toLocaleDateString()}</p>
                    </div>
                    <button onClick={() => deleteNote(note.note_id)} className="p-1.5 rounded-lg hover:bg-red-50 text-red-500 shrink-0">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </SidebarLayout>
  );
}
