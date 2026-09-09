import React, { useState, useEffect } from 'react';
import { Calendar, Plus, Trash2, Edit2, Clock, CheckCircle2, AlertCircle, Scale, Search } from 'lucide-react';
import api from '../api/api';

const STATUS_COLORS = {
  Pending: 'bg-yellow-100 text-yellow-700',
  Admitted: 'bg-blue-100 text-blue-700',
  Dismissed: 'bg-red-100 text-red-700',
  Disposed: 'bg-green-100 text-green-700',
  Stayed: 'bg-purple-100 text-purple-700',
};

const PRIORITY_COLORS = {
  Low: 'text-gray-500',
  Medium: 'text-orange-500',
  High: 'text-red-500',
  Urgent: 'text-red-700 animate-pulse',
};

export default function CaseDiaryPage() {
  const [cases, setCases] = useState([]);
  const [stats, setStats] = useState({ total_cases: 0, pending: 0, disposed: 0, upcoming_hearings: 0, pending_tasks: 0 });
  const [showForm, setShowForm] = useState(false);
  const [editingCase, setEditingCase] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [loading, setLoading] = useState(true);

  const [form, setForm] = useState({
    case_number: '', title: '', court: '', judge: '', party_petitioner: '', party_respondent: '',
    case_type: 'Civil', status: 'Pending', filing_date: '', next_hearing_date: '', description: '', priority: 'Medium',
  });

  useEffect(() => {
    fetchCases();
    fetchStats();
  }, [filterStatus, searchQuery]);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const res = await api.get('/diary/cases', {
        params: { status: filterStatus || undefined, keyword: searchQuery || undefined, limit: 100 }
      });
      setCases(res.data.data || []);
    } catch (e) {}
    setLoading(false);
  };

  const fetchStats = async () => {
    try {
      const res = await api.get('/diary/stats');
      setStats(res.data);
    } catch (e) {}
  };

  const handleSubmit = async () => {
    try {
      if (editingCase) {
        await api.put(`/diary/cases/${editingCase.id}`, form);
      } else {
        await api.post('/diary/cases', form);
      }
      setShowForm(false);
      setEditingCase(null);
      setForm({ case_number: '', title: '', court: '', judge: '', party_petitioner: '', party_respondent: '', case_type: 'Civil', status: 'Pending', filing_date: '', next_hearing_date: '', description: '', priority: 'Medium' });
      fetchCases();
      fetchStats();
    } catch (e) {
      alert('Error saving case');
    }
  };

  const deleteCase = async (id) => {
    if (!confirm('Delete this case and all related hearings/tasks?')) return;
    try {
      await api.delete(`/diary/cases/${id}`);
      fetchCases();
      fetchStats();
    } catch (e) {}
  };

  const editCase = (c) => {
    setEditingCase(c);
    setForm({ ...c });
    setShowForm(true);
  };

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2" style={{ color: 'var(--text-h)' }}>
          <Calendar className="w-6 h-6 text-emerald-600" />
          Case Diary
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text)' }}>
          Track court cases, hearings, and deadlines
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        {[
          { label: 'Total Cases', value: stats.total_cases, icon: Scale, color: 'text-blue-600' },
          { label: 'Pending', value: stats.pending, icon: Clock, color: 'text-yellow-600' },
          { label: 'Disposed', value: stats.disposed, icon: CheckCircle2, color: 'text-green-600' },
          { label: 'Upcoming Hearings', value: stats.upcoming_hearings, icon: Calendar, color: 'text-purple-600' },
          { label: 'Pending Tasks', value: stats.pending_tasks, icon: AlertCircle, color: 'text-red-600' },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-xl p-3 border shadow-sm">
            <div className="flex items-center gap-2">
              <s.icon className={`w-4 h-4 ${s.color}`} />
              <span className="text-xs font-medium text-gray-500">{s.label}</span>
            </div>
            <p className="text-xl font-bold mt-1" style={{ color: 'var(--text-h)' }}>{s.value}</p>
          </div>
        ))}
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search cases..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          />
        </div>
        <select
          value={filterStatus}
          onChange={e => setFilterStatus(e.target.value)}
          className="px-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
        >
          <option value="">All Status</option>
          <option value="Pending">Pending</option>
          <option value="Admitted">Admitted</option>
          <option value="Dismissed">Dismissed</option>
          <option value="Disposed">Disposed</option>
          <option value="Stayed">Stayed</option>
        </select>
        <button
          onClick={() => { setShowForm(true); setEditingCase(null); }}
          className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Add Case
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400">Loading cases...</div>
      ) : cases.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed rounded-xl">
          <Scale className="w-12 h-12 mx-auto mb-2 text-gray-300" />
          <p className="text-gray-500 text-sm">No cases found. Add your first case.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Case</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Parties</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Court</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Next Hearing</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody>
                {cases.map(c => (
                  <tr key={c.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="font-medium">{c.case_number}</div>
                      <div className="text-xs text-gray-500">{c.title}</div>
                      <div className={`text-xs inline-block mt-1 ${PRIORITY_COLORS[c.priority]}`}>
                        {c.priority}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs">
                      <div><span className="text-gray-400">P:</span> {c.party_petitioner}</div>
                      <div><span className="text-gray-400">R:</span> {c.party_respondent}</div>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-600">{c.court}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[c.status] || 'bg-gray-100'}`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs">
                      {c.next_hearing_date ? (
                        <span className={c.next_hearing_date < new Date().toISOString().slice(0,10) ? 'text-red-500 font-medium' : ''}>
                          {c.next_hearing_date}
                        </span>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button onClick={() => editCase(c)} className="p-1 hover:bg-gray-200 rounded mr-1">
                        <Edit2 className="w-3.5 h-3.5 text-gray-500" />
                      </button>
                      <button onClick={() => deleteCase(c.id)} className="p-1 hover:bg-red-100 rounded">
                        <Trash2 className="w-3.5 h-3.5 text-red-500" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
            <h2 className="text-lg font-bold mb-4">{editingCase ? 'Edit Case' : 'Add New Case'}</h2>
            <div className="space-y-3">
              {[
                { key: 'case_number', label: 'Case Number', placeholder: 'e.g. Crl.A. 123/2024' },
                { key: 'title', label: 'Title', placeholder: 'Case title' },
                { key: 'court', label: 'Court', placeholder: 'e.g. Lahore High Court' },
                { key: 'judge', label: 'Judge (optional)', placeholder: 'Honorable Judge Name' },
                { key: 'party_petitioner', label: 'Petitioner/Plaintiff', placeholder: 'Party name' },
                { key: 'party_respondent', label: 'Respondent/Defendant', placeholder: 'Party name' },
              ].map(field => (
                <div key={field.key}>
                  <label className="block text-xs font-medium mb-1">{field.label}</label>
                  <input
                    type="text"
                    value={form[field.key] || ''}
                    onChange={e => setForm({ ...form, [field.key]: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
                    placeholder={field.placeholder}
                  />
                </div>
              ))}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium mb-1">Case Type</label>
                  <select value={form.case_type} onChange={e => setForm({ ...form, case_type: e.target.value })} className="w-full px-3 py-2 rounded-lg border text-sm">
                    <option>Civil</option><option>Criminal</option><option>Constitutional</option>
                    <option>Family</option><option>Tax</option><option>Corporate</option>
                    <option>Property</option><option>Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1">Status</label>
                  <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })} className="w-full px-3 py-2 rounded-lg border text-sm">
                    <option>Pending</option><option>Admitted</option><option>Dismissed</option>
                    <option>Disposed</option><option>Stayed</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium mb-1">Filing Date</label>
                  <input type="date" value={form.filing_date || ''} onChange={e => setForm({ ...form, filing_date: e.target.value })} className="w-full px-3 py-2 rounded-lg border text-sm" />
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1">Next Hearing</label>
                  <input type="date" value={form.next_hearing_date || ''} onChange={e => setForm({ ...form, next_hearing_date: e.target.value })} className="w-full px-3 py-2 rounded-lg border text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">Priority</label>
                <select value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })} className="w-full px-3 py-2 rounded-lg border text-sm">
                  <option>Low</option><option>Medium</option><option>High</option><option>Urgent</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">Description</label>
                <textarea value={form.description || ''} onChange={e => setForm({ ...form, description: e.target.value })} rows={3} className="w-full px-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400" placeholder="Case details..." />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={handleSubmit} className="flex-1 py-2.5 bg-emerald-600 text-white rounded-lg font-medium text-sm hover:bg-emerald-700">
                {editingCase ? 'Update Case' : 'Add Case'}
              </button>
              <button onClick={() => { setShowForm(false); setEditingCase(null); }} className="flex-1 py-2.5 border rounded-lg font-medium text-sm hover:bg-gray-50">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
