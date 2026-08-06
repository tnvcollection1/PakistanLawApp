import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  CheckSquare, Plus, Calendar, Clock, AlertTriangle,
  Loader2, Save, Trash2, Briefcase
} from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import SidebarLayout from '../components/SidebarLayout';
import { PageTransition, FadeInUp } from '../components/Animations';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const priorityConfig = {
  high: { label: 'High', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400', dot: 'bg-red-500' },
  medium: { label: 'Medium', color: 'bg-primary/20 text-primary dark:bg-primary/30 dark:text-primary', dot: 'bg-primary' },
  low: { label: 'Low', color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400', dot: 'bg-green-500' },
};

const statusConfig = {
  pending: { label: 'To Do', color: 'bg-muted text-muted-foreground dark:text-muted-foreground dark:bg-muted-foreground dark:text-muted-foreground' },
  in_progress: { label: 'In Progress', color: 'bg-primary/10 text-slate-900 dark:text-foreground dark:bg-primary/30 dark:text-primary' },
  completed: { label: 'Done', color: 'bg-emerald-100 text-primary dark:text-primary dark:bg-emerald-900/30 dark:text-emerald-400' },
};

const TaskBoard = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [editTask, setEditTask] = useState(null);
  const [matters, setMatters] = useState([]);
  const [form, setForm] = useState({ title: '', matter_id: '', assigned_to: '', due_date: '', priority: 'medium', status: 'pending', description: '' });
  const [saving, setSaving] = useState(false);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (statusFilter !== 'all') params.set('status', statusFilter);
    if (priorityFilter !== 'all') params.set('priority', priorityFilter);
    const matterId = searchParams.get('matter');
    if (matterId) params.set('matter_id', matterId);
    try {
      const res = await fetch(`${API}/enterprise/tasks?${params}`);
      const data = await res.json();
      setTasks(data.data || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [statusFilter, priorityFilter, searchParams]);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);
  useEffect(() => {
    fetch(`${API}/enterprise/matters?limit=200`).then(r => r.json()).then(d => setMatters(d.data || [])).catch(console.error);
  }, []);

  const openNew = () => {
    setEditTask(null);
    setForm({ title: '', matter_id: searchParams.get('matter') || '', assigned_to: '', due_date: '', priority: 'medium', status: 'pending', description: '' });
    setShowForm(true);
  };

  const openEdit = (t) => {
    setEditTask(t);
    setForm({ title: t.title, matter_id: t.matter_id || '', assigned_to: t.assigned_to || '', due_date: t.due_date || '', priority: t.priority || 'medium', status: t.status || 'pending', description: t.description || '' });
    setShowForm(true);
  };

  const handleSave = async () => {
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      const method = editTask ? 'PUT' : 'POST';
      const url = editTask ? `${API}/enterprise/tasks/${editTask.id}` : `${API}/enterprise/tasks`;
      await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) });
      setShowForm(false);
      fetchTasks();
    } catch (e) { console.error(e); }
    finally { setSaving(false); }
  };

  const handleDelete = async (taskId) => {
    if (!window.confirm('Delete this task?')) return;
    await fetch(`${API}/enterprise/tasks/${taskId}`, { method: 'DELETE' });
    fetchTasks();
  };

  const toggleStatus = async (task) => {
    const next = task.status === 'pending' ? 'in_progress' : task.status === 'in_progress' ? 'completed' : 'pending';
    await fetch(`${API}/enterprise/tasks/${task.id}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...task, status: next, matter_title: undefined })
    });
    fetchTasks();
  };

  const isOverdue = (t) => t.due_date && t.status !== 'completed' && new Date(t.due_date) < new Date();

  // Group tasks by status for kanban-like layout
  const grouped = { pending: [], in_progress: [], completed: [] };
  tasks.forEach(t => { if (grouped[t.status]) grouped[t.status].push(t); else grouped.pending.push(t); });

  return (
    <SidebarLayout>
      <PageTransition>
      <div className="min-h-screen bg-background dark:bg-background" data-testid="task-board">
        <div className="bg-white dark:bg-background border-b border-muted dark:border-border px-6 md:px-10 py-6">
          <div className="max-w-screen-2xl mx-auto flex items-center justify-between">
            <FadeInUp>
              <h1 className="font-serif text-2xl md:text-3xl font-bold text-slate-900 dark:text-primary-foreground flex items-center gap-3">
                <CheckSquare className="text-primary" size={24} /> Task Board
              </h1>
              <p className="text-sm text-muted-foreground dark:text-muted-foreground mt-2">{tasks.length} tasks</p>
            </FadeInUp>
            <Button onClick={openNew} className="bg-primary hover:bg-primary text-primary-foreground" data-testid="new-task-btn">
              <Plus size={16} className="mr-2" /> New Task
            </Button>
          </div>
        </div>

        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-8">

        {/* Filters */}
        <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-4 mb-4">
          <div className="flex gap-3">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40"><SelectValue placeholder="Status" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                {Object.entries(statusConfig).map(([k, v]) => <SelectItem key={k} value={k}>{v.label}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-40"><SelectValue placeholder="Priority" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priority</SelectItem>
                {Object.entries(priorityConfig).map(([k, v]) => <SelectItem key={k} value={k}>{v.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="animate-spin text-primary" size={40} /></div>
        ) : tasks.length === 0 ? (
          <div className="bg-white dark:bg-background rounded-xl border border-muted dark:border-border p-12 text-center">
            <CheckSquare size={48} className="mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg text-foreground dark:text-muted-foreground">No tasks yet</p>
            <Button onClick={openNew} className="mt-4 bg-background text-primary-foreground">Create Your First Task</Button>
          </div>
        ) : (
          /* Kanban Columns */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {Object.entries(statusConfig).map(([status, cfg]) => (
              <div key={status}>
                <div className="flex items-center gap-2 mb-3">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${cfg.color}`}>{cfg.label}</span>
                  <span className="text-xs text-muted-foreground">{grouped[status]?.length || 0}</span>
                </div>
                <div className="space-y-2">
                  {(grouped[status] || []).map((t, i) => (
                    <div
                      key={i}
                      className={`bg-white dark:bg-background rounded-lg border p-3 hover:shadow-md transition-all cursor-pointer ${
                        isOverdue(t) ? 'border-red-300 dark:border-red-700' : 'border-muted dark:border-border'
                      }`}
                      data-testid={`task-card-${t.id}`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <button onClick={() => toggleStatus(t)} className="text-sm font-medium text-slate-900 dark:text-primary-foreground text-left flex-1 hover:text-slate-800 dark:text-foreground">
                          {t.title}
                        </button>
                        <div className="flex gap-1 ml-2">
                          <button onClick={() => openEdit(t)} className="text-muted-foreground hover:text-slate-800 dark:text-foreground"><CheckSquare size={12} /></button>
                          <button onClick={() => handleDelete(t.id)} className="text-muted-foreground hover:text-red-600"><Trash2 size={12} /></button>
                        </div>
                      </div>
                      {t.matter_title && (
                        <p className="text-xs text-muted-foreground dark:text-muted-foreground flex items-center gap-1 mb-2"><Briefcase size={10} />{t.matter_title}</p>
                      )}
                      <div className="flex items-center justify-between">
                        <span className={`text-xs px-1.5 py-0.5 rounded ${priorityConfig[t.priority]?.color || priorityConfig.medium.color}`}>
                          {t.priority}
                        </span>
                        {t.due_date && (
                          <span className={`text-xs flex items-center gap-1 ${isOverdue(t) ? 'text-red-600 font-medium' : 'text-muted-foreground'}`}>
                            {isOverdue(t) && <AlertTriangle size={10} />}
                            <Calendar size={10} />
                            {new Date(t.due_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Task Form Modal */}
        <Dialog open={showForm} onOpenChange={setShowForm}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>{editTask ? 'Edit Task' : 'New Task'}</DialogTitle>
              <DialogDescription className="sr-only">Task form</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground dark:text-muted-foreground mb-1 block">Title *</label>
                <Input value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} placeholder="e.g., File Written Arguments" data-testid="task-title-input" />
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground dark:text-muted-foreground mb-1 block">Linked Matter</label>
                <Select value={form.matter_id || 'none'} onValueChange={v => setForm({ ...form, matter_id: v === 'none' ? '' : v })}>
                  <SelectTrigger><SelectValue placeholder="Select matter..." /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">No Matter</SelectItem>
                    {matters.map(m => <SelectItem key={m.id} value={m.id}>{m.title}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground dark:text-muted-foreground mb-1 block">Priority</label>
                  <Select value={form.priority} onValueChange={v => setForm({ ...form, priority: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {Object.entries(priorityConfig).map(([k, v]) => <SelectItem key={k} value={k}>{v.label}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground dark:text-muted-foreground mb-1 block">Status</label>
                  <Select value={form.status} onValueChange={v => setForm({ ...form, status: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {Object.entries(statusConfig).map(([k, v]) => <SelectItem key={k} value={k}>{v.label}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground dark:text-muted-foreground mb-1 block">Due Date</label>
                  <Input type="date" value={form.due_date} onChange={e => setForm({ ...form, due_date: e.target.value })} />
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground dark:text-muted-foreground mb-1 block">Assigned To</label>
                  <Input value={form.assigned_to} onChange={e => setForm({ ...form, assigned_to: e.target.value })} placeholder="Name" />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground dark:text-muted-foreground mb-1 block">Description</label>
                <textarea value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} rows={2}
                  className="w-full rounded-md border border-muted dark:border-border bg-white dark:bg-background px-3 py-2 text-sm" />
              </div>
              <div className="flex gap-3 pt-2">
                <Button onClick={handleSave} disabled={saving || !form.title.trim()} className="bg-primary hover:bg-primary text-primary-foreground" data-testid="save-task-btn">
                  {saving ? <Loader2 size={16} className="animate-spin mr-2" /> : <Save size={16} className="mr-2" />}
                  {editTask ? 'Update' : 'Create'}
                </Button>
                <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
        </div>
      </div>
      </PageTransition>
    </SidebarLayout>
  );
};

export default TaskBoard;
