import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import SidebarLayout from '../components/SidebarLayout';
import { useAuth } from '../context/AuthContext';
import { BookOpen, Plus, Trash2, Loader2, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function ReadingListsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [lists, setLists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user?.username) fetchLists();
  }, [user]);

  const fetchLists = async () => {
    try {
      const res = await fetch(`${API}/api/reading-lists?username=${user.username}`);
      if (res.ok) setLists(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const createList = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      const res = await fetch(`${API}/api/reading-lists`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user.username, name: name.trim() }),
      });
      if (res.ok) {
        setName(''); setShowForm(false);
        fetchLists();
      }
    } catch (e) { console.error(e); }
    finally { setSaving(false); }
  };

  const deleteList = async (listId) => {
    try {
      await fetch(`${API}/api/reading-lists/${listId}`, { method: 'DELETE' });
      setLists(prev => prev.filter(l => l.list_id !== listId));
    } catch (e) { console.error(e); }
  };

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background">
        <div className="bg-white dark:bg-background border-b shadow-sm px-4 sm:px-6 py-4 sm:py-5">
          <div className="max-w-4xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h1 className="text-lg sm:text-xl font-semibold text-slate-800 dark:text-foreground flex items-center gap-2">
                <BookOpen size={20} className="text-slate-800 dark:text-foreground" /> Reading Lists
              </h1>
              <p className="text-xs sm:text-sm text-muted-foreground mt-1">Organize cases into custom collections</p>
            </div>
            <Button onClick={() => setShowForm(!showForm)} className="bg-background hover:bg-card w-full sm:w-auto">
              <Plus size={14} className="mr-1" /> New List
            </Button>
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4 sm:py-8 space-y-4">
          {showForm && (
            <Card>
              <CardHeader><CardTitle className="text-lg">Create Reading List</CardTitle></CardHeader>
              <CardContent>
                <form onSubmit={createList} className="flex gap-2">
                  <input
                    type="text" value={name} onChange={e => setName(e.target.value)}
                    placeholder="List name..."
                    className="flex-1 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <Button type="submit" disabled={saving} className="bg-background hover:bg-card">
                    {saving ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
                </form>
              </CardContent>
            </Card>
          )}

          {loading ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
          ) : lists.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                <BookOpen size={40} className="text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">No reading lists yet</h3>
                <p className="text-sm text-muted-foreground mb-4">Create lists to organize your research</p>
                <Button onClick={() => setShowForm(true)} className="bg-background hover:bg-card">
                  <Plus size={14} className="mr-1" /> Create List
                </Button>
              </CardContent>
            </Card>
          ) : (
            lists.map(list => (
              <Card key={list.list_id} className="hover:bg-card cursor-pointer transition-colors" onClick={() => navigate(`/reading-list/${list.list_id}`)}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <BookOpen size={16} className="text-primary" />
                      </div>
                      <div>
                        <h3 className="font-medium text-foreground">{list.name}</h3>
                        <p className="text-sm text-muted-foreground">{list.case_count || 0} cases</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <ArrowRight size={16} className="text-muted-foreground" />
                      <button
                        onClick={(e) => { e.stopPropagation(); deleteList(list.list_id); }}
                        className="p-1.5 rounded-lg hover:bg-red-50 text-red-500"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
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
