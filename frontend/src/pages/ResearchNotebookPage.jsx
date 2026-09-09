import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Trash2, Search, Tag, Clock, X, Save, Edit2, StickyNote } from 'lucide-react';
import api from '../api/api';

const COLORS = [
  '#fef9c3', '#dbeafe', '#dcfce7', '#fce7f3', '#f3e8ff', '#ffedd5',
  '#fee2e2', '#e0e7ff', '#ccfbf1', '#ecfccb',
];

export default function ResearchNotebookPage() {
  const [notes, setNotes] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingNote, setEditingNote] = useState(null);
  const [loading, setLoading] = useState(true);

  const [form, setForm] = useState({
    title: '', content: '', reference_id: '', reference_type: 'caselaw', reference_title: '', color: '#fef9c3',
  });

  useEffect(() => {
    fetchNotes();
  }, [searchQuery]);

  const fetchNotes = async () => {
    try {
      setLoading(true);
      const res = await api.get('/notes', {
        params: { keyword: searchQuery || undefined, limit: 100 }
      });
      setNotes(res.data.data || []);
    } catch (e) {}
    setLoading(false);
  };

  const handleSubmit = async () => {
    try {
      if (editingNote) {
        await api.put(`/notes/${editingNote.id}`, null, {
          params: { title: form.title, content: form.content, color: form.color }
        });
      } else {
        await api.post('/notes', null, {
          params: {
            reference_id: form.reference_id || 'notebook-' + Date.now(),
            reference_type: form.reference_type,
            reference_title: form.reference_title || form.title,
            title: form.title,
            content: form.content,
            color: form.color,
          }
        });
      }
      setShowForm(false);
      setEditingNote(null);
      setForm({ title: '', content: '', reference_id: '', reference_type: 'caselaw', reference_title: '', color: '#fef9c3' });
      fetchNotes();
    } catch (e) {
      alert('Error saving note');
    }
  };

  const deleteNote = async (id) => {
    if (!confirm('Delete this note?')) return;
    try {
      await api.delete(`/notes/${id}`);
      fetchNotes();
    } catch (e) {}
  };

  const editNote = (note) => {
    setEditingNote(note);
    setForm({
      title: note.title || '',
      content: note.content || '',
      reference_id: note.reference_id || '',
      reference_type: note.reference_type || 'caselaw',
      reference_title: note.reference_title || '',
      color: note.color || '#fef9c3',
    });
    setShowForm(true);
  };

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2" style={{ color: 'var(--text-h)' }}>
          <BookOpen className="w-6 h-6 text-emerald-600" />
          Research Notebook
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text)' }}>
          Save and organize your legal research notes
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input type="text" placeholder="Search notes..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} className="w-full pl-9 pr-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400" />
        </div>
        <button onClick={() => { setShowForm(true); setEditingNote(null); }} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 flex items-center gap-2">
          <Plus className="w-4 h-4" /> New Note
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400">Loading notes...</div>
      ) : notes.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed rounded-xl">
          <StickyNote className="w-12 h-12 mx-auto mb-2 text-gray-300" />
          <p className="text-gray-500 text-sm">No notes yet. Create your first research note.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {notes.map(note => (
            <div key={note.id} className="rounded-xl border p-4 hover:shadow-md transition-shadow" style={{ backgroundColor: note.color || '#fef9c3' }}>
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-sm line-clamp-1 flex-1">{note.title || 'Untitled'}</h3>
                <div className="flex gap-1 ml-2">
                  <button onClick={() => editNote(note)} className="p-1 hover:bg-black/10 rounded"><Edit2 className="w-3 h-3 text-gray-600" /></button>
                  <button onClick={() => deleteNote(note.id)} className="p-1 hover:bg-black/10 rounded"><Trash2 className="w-3 h-3 text-red-500" /></button>
                </div>
              </div>
              <p className="text-xs line-clamp-4 mb-3 whitespace-pre-wrap">{note.content}</p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center gap-1"><Tag className="w-3 h-3" /><span className="capitalize">{note.reference_type}</span></div>
                <div className="flex items-center gap-1"><Clock className="w-3 h-3" /><span>{new Date(note.created_at).toLocaleDateString()}</span></div>
              </div>
              {note.reference_title && <div className="text-xs text-gray-500 mt-1 truncate">Ref: {note.reference_title}</div>}
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-lg p-6">
            <h2 className="text-lg font-bold mb-4">{editingNote ? 'Edit Note' : 'New Research Note'}</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium mb-1">Title</label>
                <input type="text" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} className="w-full px-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400" placeholder="Note title" />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">Content</label>
                <textarea value={form.content} onChange={e => setForm({ ...form, content: e.target.value })} rows={6} className="w-full px-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400" placeholder="Your research notes..." />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium mb-1">Reference Type</label>
                  <select value={form.reference_type} onChange={e => setForm({ ...form, reference_type: e.target.value })} className="w-full px-3 py-2 rounded-lg border text-sm">
                    <option value="caselaw">Case Law</option>
                    <option value="statute">Statute</option>
                    <option value="term">Legal Term</option>
                    <option value="general">General</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1">Reference ID/Title</label>
                  <input type="text" value={form.reference_title} onChange={e => setForm({ ...form, reference_title: e.target.value })} className="w-full px-3 py-2 rounded-lg border text-sm" placeholder="e.g. 2023 SCMR 1234" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">Color</label>
                <div className="flex gap-2 flex-wrap">
                  {COLORS.map(c => (
                    <button key={c} onClick={() => setForm({ ...form, color: c })} className={`w-8 h-8 rounded-full border-2 ${form.color === c ? 'border-gray-800 scale-110' : 'border-transparent'}`} style={{ backgroundColor: c }} />
                  ))}
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={handleSubmit} className="flex-1 py-2.5 bg-emerald-600 text-white rounded-lg font-medium text-sm hover:bg-emerald-700 flex items-center justify-center gap-2">
                <Save className="w-4 h-4" />{editingNote ? 'Update Note' : 'Save Note'}
              </button>
              <button onClick={() => { setShowForm(false); setEditingNote(null); }} className="flex-1 py-2.5 border rounded-lg font-medium text-sm hover:bg-gray-50">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
