import React, { useState, useEffect } from 'react';
import { Bell, Plus, Trash2, Loader2, Search, Gavel, Building, Hash, ToggleLeft, ToggleRight, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import SidebarLayout from '../components/SidebarLayout';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || '';

const ALERT_TYPES = [
  { value: 'court', label: 'Court', icon: Building, placeholder: 'e.g., Supreme Court' },
  { value: 'judge', label: 'Judge', icon: Gavel, placeholder: 'e.g., Justice Isa' },
  { value: 'keyword', label: 'Keyword', icon: Search, placeholder: 'e.g., bail, murder, fraud' },
  { value: 'topic', label: 'Topic', icon: Hash, placeholder: 'e.g., constitutional rights' },
];

export default function AlertsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState('');
  const [alertType, setAlertType] = useState('keyword');
  const [value, setValue] = useState('');
  const [frequency, setFrequency] = useState('daily');
  const [creating, setCreating] = useState(false);
  const [expandedAlert, setExpandedAlert] = useState(null);
  const [matches, setMatches] = useState({});
  const [matchLoading, setMatchLoading] = useState(null);

  useEffect(() => {
    if (user?.username) fetchAlerts();
  }, [user]);

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${API}/api/alerts?username=${user.username}`);
      if (res.ok) setAlerts(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const createAlert = async (e) => {
    e.preventDefault();
    if (!name.trim() || !value.trim()) return;
    setCreating(true);
    try {
      const res = await fetch(`${API}/api/alerts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: user.username,
          name: name.trim(),
          alert_type: alertType,
          value: value.trim(),
          frequency,
        }),
      });
      if (res.ok) {
        setName(''); setValue(''); setShowCreate(false);
        fetchAlerts();
      }
    } catch (e) { console.error(e); }
    finally { setCreating(false); }
  };

  const toggleAlert = async (alertId, currentEnabled) => {
    try {
      await fetch(`${API}/api/alerts/${alertId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !currentEnabled }),
      });
      setAlerts(prev => prev.map(a =>
        a.alert_id === alertId ? { ...a, enabled: !currentEnabled } : a
      ));
    } catch (e) { console.error(e); }
  };

  const deleteAlert = async (alertId) => {
    try {
      await fetch(`${API}/api/alerts/${alertId}`, { method: 'DELETE' });
      setAlerts(prev => prev.filter(a => a.alert_id !== alertId));
    } catch (e) { console.error(e); }
  };

  const checkMatches = async (alertId) => {
    if (expandedAlert === alertId) { setExpandedAlert(null); return; }
    setExpandedAlert(alertId);
    setMatchLoading(alertId);
    try {
      const res = await fetch(`${API}/api/alerts/${alertId}/matches?limit=10`);
      if (res.ok) {
        const data = await res.json();
        setMatches(prev => ({ ...prev, [alertId]: data }));
      }
    } catch (e) { console.error(e); }
    finally { setMatchLoading(null); }
  };

  const typeConfig = ALERT_TYPES.find(t => t.value === alertType);

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background" data-testid="alerts-page">
        <div className="bg-white dark:bg-background border-b shadow-sm px-4 sm:px-6 py-4 sm:py-5">
          <div className="max-w-4xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h1 className="text-lg sm:text-xl font-semibold text-slate-800 dark:text-foreground flex items-center gap-2" data-testid="alerts-title">
                <Bell size={20} className="text-slate-800 dark:text-foreground" /> Case Law Alerts
              </h1>
              <p className="text-xs sm:text-sm text-muted-foreground dark:text-muted-foreground mt-1">Get notified when new cases match your criteria</p>
            </div>
            <Button onClick={() => setShowCreate(!showCreate)} className="bg-background hover:bg-card w-full sm:w-auto" data-testid="create-alert-btn">
              <Plus size={14} className="mr-1" /> New Alert
            </Button>
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4 sm:py-8 space-y-6">
          {/* Create Alert Form */}
          {showCreate && (
            <Card data-testid="create-alert-form">
              <CardHeader><CardTitle className="text-lg">Create New Alert</CardTitle></CardHeader>
              <CardContent>
                <form onSubmit={createAlert} className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-foreground dark:text-muted-foreground mb-1.5 block">Alert Name</label>
                    <input
                      type="text" value={name} onChange={(e) => setName(e.target.value)}
                      placeholder="e.g., Bail Cases in Supreme Court"
                      className="w-full px-3 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      data-testid="alert-name-input"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground dark:text-muted-foreground mb-1.5 block">Alert Type</label>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      {ALERT_TYPES.map((t) => (
                        <button key={t.value} type="button"
                          onClick={() => setAlertType(t.value)}
                          data-testid={`alert-type-${t.value}`}
                          className={`p-2.5 rounded-lg border text-sm flex items-center gap-2 transition-colors ${
                            alertType === t.value ? 'bg-primary/10/50 border-primary text-slate-900 dark:text-foreground' : 'hover:bg-background'
                          }`}>
                          <t.icon size={14} /> {t.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground dark:text-muted-foreground mb-1.5 block">Search Value</label>
                    <input
                      type="text" value={value} onChange={(e) => setValue(e.target.value)}
                      placeholder={typeConfig?.placeholder}
                      className="w-full px-3 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      data-testid="alert-value-input"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground dark:text-muted-foreground mb-1.5 block">Frequency</label>
                    <div className="flex gap-2">
                      {['daily', 'weekly'].map(f => (
                        <button key={f} type="button" onClick={() => setFrequency(f)}
                          className={`px-4 py-2 rounded-lg border text-sm capitalize ${
                            frequency === f ? 'bg-primary/10/50 border-primary text-slate-900 dark:text-foreground' : 'hover:bg-background'
                          }`}>
                          {f}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-2 pt-2">
                    <Button type="submit" disabled={creating} className="bg-background hover:bg-card" data-testid="save-alert-btn">
                      {creating ? <Loader2 size={14} className="animate-spin mr-1" /> : <Bell size={14} className="mr-1" />}
                      Create Alert
                    </Button>
                    <Button type="button" variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {/* Alert List */}
          {loading ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
          ) : alerts.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                <Bell size={40} className="text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium text-foreground dark:text-muted-foreground mb-2">No alerts yet</h3>
                <p className="text-sm text-muted-foreground mb-4">Create an alert to get notified about new cases</p>
                <Button onClick={() => setShowCreate(true)} className="bg-background hover:bg-card">
                  <Plus size={14} className="mr-1" /> Create Your First Alert
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {alerts.map((alert) => (
                <Card key={alert.alert_id} data-testid={`alert-${alert.alert_id}`}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                          {(() => {
                            const Icon = ALERT_TYPES.find(t => t.value === alert.alert_type)?.icon || Bell;
                            return <Icon size={16} className="text-primary" />;
                          })()}
                        </div>
                        <div>
                          <h3 className="font-medium text-foreground">{alert.name}</h3>
                          <p className="text-sm text-muted-foreground">
                            {ALERT_TYPES.find(t => t.value === alert.alert_type)?.label}: {alert.value}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => toggleAlert(alert.alert_id, alert.enabled)}
                          data-testid={`toggle-alert-${alert.alert_id}`}
                          className="p-1.5 rounded-lg hover:bg-background"
                        >
                          {alert.enabled ? <ToggleRight size={20} className="text-green-600" /> : <ToggleLeft size={20} className="text-slate-400" />}
                        </button>
                        <button
                          onClick={() => checkMatches(alert.alert_id)}
                          data-testid={`check-matches-${alert.alert_id}`}
                          className="p-1.5 rounded-lg hover:bg-background"
                        >
                          {expandedAlert === alert.alert_id ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                        </button>
                        <button
                          onClick={() => deleteAlert(alert.alert_id)}
                          data-testid={`delete-alert-${alert.alert_id}`}
                          className="p-1.5 rounded-lg hover:bg-red-50 text-red-500"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>

                    {expandedAlert === alert.alert_id && (
                      <div className="mt-4 pt-4 border-t">
                        {matchLoading === alert.alert_id ? (
                          <div className="flex justify-center py-6"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>
                        ) : matches[alert.alert_id]?.length > 0 ? (
                          <div className="space-y-2">
                            <h4 className="text-sm font-medium mb-2">Recent Matches ({matches[alert.alert_id].length})</h4>
                            {matches[alert.alert_id].map((match) => (
                              <div
                                key={match.case_id}
                                onClick={() => navigate(`/case/${match.case_id}`)}
                                className="p-3 rounded-lg bg-background hover:bg-card cursor-pointer"
                              >
                                <p className="text-sm font-medium">{match.title}</p>
                                <div className="flex items-center gap-2 mt-1">
                                  <Badge variant="secondary" className="text-xs">{match.court}</Badge>
                                  <span className="text-xs text-muted-foreground">{match.date}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-muted-foreground text-center py-4">No matching cases found yet</p>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </SidebarLayout>
  );
}
