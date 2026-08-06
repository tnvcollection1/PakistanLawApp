import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Database, Cpu, TrendingUp, Layers, Clock, CheckCircle, XCircle, RefreshCw, BarChart3, Zap } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const Stat = ({ label, value, sub, icon: Icon, color = 'text-primary' }) => (
  <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50 dark:bg-muted/20">
    {Icon && <Icon size={18} className={`mt-0.5 ${color}`} />}
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-lg font-bold font-mono">{typeof value === 'number' ? value.toLocaleString() : value}</p>
      {sub && <p className="text-xs text-muted-foreground mt-0.5">{sub}</p>}
    </div>
  </div>
);

const ProgressRing = ({ pct, size = 80, stroke = 6, label }) => {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;
  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="currentColor" strokeWidth={stroke} className="text-muted/30" />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="currentColor" strokeWidth={stroke}
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
          className={pct >= 100 ? 'text-emerald-500' : pct > 50 ? 'text-primary' : 'text-amber-500'}
          style={{ transition: 'stroke-dashoffset 0.6s ease' }} />
      </svg>
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="text-sm font-bold">{pct.toFixed(1)}%</span>
    </div>
  );
};

const LogViewer = ({ lines, title }) => (
  <div className="mt-3">
    <p className="text-xs font-medium text-muted-foreground mb-1">{title}</p>
    <div className="bg-slate-950 rounded-lg p-3 max-h-40 overflow-y-auto font-mono text-xs text-emerald-400 space-y-0.5">
      {lines.length === 0 ? <p className="text-muted-foreground">No logs available</p> :
        lines.map((l, i) => <p key={i} className="break-all">{l}</p>)}
    </div>
  </div>
);

const MonitorDashboard = () => {
  const [overview, setOverview] = useState(null);
  const [spider, setSpider] = useState(null);
  const [faiss, setFaiss] = useState(null);
  const [ingestion, setIngestion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(null);

  const fetchAll = useCallback(async () => {
    try {
      const [ov, sp, fa, ing] = await Promise.all([
        fetch(`${API_URL}/api/admin/dashboard/overview`).then(r => r.json()).catch(() => null),
        fetch(`${API_URL}/api/admin/eastlaw/spider-status`).then(r => r.json()).catch(() => null),
        fetch(`${API_URL}/api/admin/faiss/status`).then(r => r.json()).catch(() => null),
        fetch(`${API_URL}/api/admin/eastlaw/ingestion-status`).then(r => r.json()).catch(() => null),
      ]);
      if (ov) setOverview(ov);
      if (sp) setSpider(sp);
      if (fa) setFaiss(fa);
      if (ing) setIngestion(ing);
      setLastRefresh(new Date());
    } catch (e) {
      console.error('Monitor fetch failed:', e);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 10000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  if (loading) return (
    <div className="flex items-center justify-center py-20" data-testid="monitor-loading">
      <RefreshCw className="animate-spin text-primary mr-2" size={20} />
      <span className="text-muted-foreground">Loading dashboard...</span>
    </div>
  );

  const db = overview?.database || {};
  const bench = overview?.competitor_benchmark || {};
  const spiderPct = spider?.target_total ? ((spider?.progress?.fetched || spider?.state?.fetched || 0) / spider.target_total) * 100 : 0;
  const contentPct = db.total_cases ? (db.cases_with_content / db.total_cases) * 100 : 0;
  const gapPct = bench.eastlaw_total ? (bench.our_total / bench.eastlaw_total) * 100 : 0;

  return (
    <div className="space-y-6" data-testid="monitor-dashboard">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity size={18} className="text-primary" />
          <span className="text-sm text-muted-foreground">Last refresh: {lastRefresh ? lastRefresh.toLocaleTimeString() : '—'} (auto-refreshes every 10s)</span>
        </div>
        <button onClick={fetchAll} className="text-xs text-primary hover:underline flex items-center gap-1" data-testid="refresh-btn"><RefreshCw size={12} /> Refresh Now</button>
      </div>
      <Card data-testid="competitor-card"><CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><TrendingUp size={16} /> vs EastLaw Benchmark</CardTitle></CardHeader><CardContent><div className="flex items-center gap-8 flex-wrap"><ProgressRing pct={Math.min(gapPct, 100)} label="vs EastLaw" /><div className="flex-1 grid grid-cols-3 gap-3"><Stat label="Our Cases" value={bench.our_total || 0} icon={Database} color="text-emerald-500" /><Stat label="EastLaw Total" value={bench.eastlaw_total || 0} icon={BarChart3} color="text-amber-500" /><Stat label={bench.ahead ? 'Ahead by' : 'Gap'} value={Math.abs(bench.gap || 0)} icon={bench.ahead ? CheckCircle : TrendingUp} color={bench.ahead ? 'text-emerald-500' : 'text-red-500'} /></div></div></CardContent></Card>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card data-testid="spider-card"><CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><Zap size={16} /> EastLaw Spider <Badge variant={spider?.running ? 'default' : 'secondary'} className="ml-auto text-xs">{spider?.running ? 'RUNNING' : 'STOPPED'}</Badge></CardTitle></CardHeader><CardContent className="space-y-3"><div className="grid grid-cols-2 gap-2"><Stat label="Fetched" value={spider?.progress?.fetched || spider?.state?.fetched || 0} icon={CheckCircle} color="text-emerald-500" /><Stat label="Queue" value={spider?.state?.queued || 0} icon={Clock} color="text-blue-500" /><Stat label="Discovered" value={spider?.progress?.discovered || 0} icon={Layers} color="text-purple-500" /><Stat label="Batches" value={spider?.batches?.count || 0} sub={`${spider?.batches?.total_size_mb || 0} MB`} icon={Database} color="text-amber-500" /></div><div className="pt-2"><div className="flex justify-between text-xs text-muted-foreground mb-1"><span>Progress</span><span className="font-mono">{spiderPct.toFixed(1)}% of 231K</span></div><div className="w-full bg-muted rounded-full h-2"><div className="bg-primary h-2 rounded-full transition-all" style={{ width: `${Math.min(spiderPct, 100)}%` }} /></div></div>{spider?.progress?.rate_per_hour && <p className="text-xs text-muted-foreground">Rate: {spider.progress.rate_per_hour?.toLocaleString()}/hr | Errors: {spider?.progress?.errors || 0}</p>}<LogViewer lines={spider?.recent_logs || []} title="Recent Spider Logs" /></CardContent></Card>
        <Card data-testid="faiss-card"><CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><Cpu size={16} /> FAISS Semantic Index {faiss?.incremental_running && <Badge className="ml-auto text-xs">UPDATING</Badge>}</CardTitle></CardHeader><CardContent className="space-y-3"><div className="grid grid-cols-2 gap-2"><Stat label="Total Vectors" value={faiss?.rebuild_progress?.total_vectors || 0} icon={Layers} color="text-purple-500" /><Stat label="Model" value={faiss?.rebuild_progress?.model || 'voyage-3-large'} icon={Cpu} color="text-blue-500" /><Stat label="Collections" value={Object.keys(faiss?.indexes || {}).length} icon={Database} color="text-emerald-500" /><Stat label="Last Rebuilt" value={faiss?.rebuild_progress?.completed_at ? new Date(faiss.rebuild_progress.completed_at).toLocaleDateString() : '—'} icon={Clock} color="text-amber-500" /></div>{faiss?.incremental_progress?.added && <div className="p-2 rounded bg-emerald-500/10 text-xs text-emerald-600 dark:text-emerald-400">Incremental update added {faiss.incremental_progress.added.toLocaleString()} new vectors. Total: {faiss.incremental_progress.total_index?.toLocaleString()}</div>}{faiss?.incremental_running && <div className="p-2 rounded bg-amber-500/10 text-xs text-amber-600 dark:text-amber-400 animate-pulse">Incremental embedding update in progress...</div>}{faiss?.indexes && Object.keys(faiss.indexes).length > 0 && <div className="mt-2"><p className="text-xs font-medium text-muted-foreground mb-1">Index Files</p><div className="space-y-1 max-h-40 overflow-y-auto">{Object.entries(faiss.indexes).sort((a, b) => b[1].size_mb - a[1].size_mb).map(([name, info]) => (<div key={name} className="flex justify-between text-xs font-mono bg-muted/50 px-2 py-1 rounded"><span>{name}</span><span className="text-muted-foreground">{info.size_mb} MB</span></div>))}</div></div>}</CardContent></Card>
        <Card data-testid="ingestion-card"><CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><Database size={16} /> Ingestion Pipeline <Badge variant={ingestion?.cron_active ? 'default' : 'secondary'} className="ml-auto text-xs">{ingestion?.cron_active ? 'CRON ACTIVE' : 'CRON OFF'}</Badge></CardTitle></CardHeader><CardContent className="space-y-3"><div className="grid grid-cols-2 gap-2"><Stat label="EastLaw Ingested" value={ingestion?.eastlaw_cases || 0} icon={CheckCircle} color="text-emerald-500" /><Stat label="Total DB Cases" value={ingestion?.total_cases || 0} icon={Database} color="text-blue-500" /></div><div className="pt-2"><div className="flex justify-between text-xs text-muted-foreground mb-1"><span>Content Coverage</span><span className="font-mono">{contentPct.toFixed(1)}%</span></div><div className="w-full bg-muted rounded-full h-2"><div className="bg-emerald-500 h-2 rounded-full transition-all" style={{ width: `${Math.min(contentPct, 100)}%` }} /></div></div><LogViewer lines={ingestion?.recent_logs || []} title="Recent Ingestion Logs" /></CardContent></Card>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card data-testid="collections-card"><CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><Database size={16} /> Database Collections</CardTitle></CardHeader><CardContent><div className="grid grid-cols-2 sm:grid-cols-3 gap-2">{[{ label: 'Case Laws', value: db.total_cases },{ label: 'Statutes', value: db.statutes },{ label: 'Dictionary', value: db.dictionary },{ label: "Black's Law", value: db.blacks_law },{ label: 'Legal Terms', value: db.legal_terms },{ label: 'Maxims', value: db.maxims },{ label: 'Words/Phrases', value: db.words_phrases },{ label: 'Articles', value: db.articles },{ label: 'Topics', value: db.topics }].map(c => (<div key={c.label} className="p-2 rounded bg-muted/50 text-center"><p className="text-xs text-muted-foreground">{c.label}</p><p className="text-sm font-bold font-mono">{(c.value || 0).toLocaleString()}</p></div>))}</div></CardContent></Card>
        <Card data-testid="courts-card"><CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><BarChart3 size={16} /> Top Courts</CardTitle></CardHeader><CardContent><div className="space-y-2">{(overview?.courts || []).slice(0, 8).map((c, i) => { const maxCount = overview?.courts?.[0]?.count || 1; const pct = (c.count / maxCount) * 100; return (<div key={i} className="flex items-center gap-2"><span className="text-xs text-muted-foreground w-36 truncate">{c.name}</span><div className="flex-1 bg-muted rounded-full h-2 overflow-hidden"><div className="bg-primary/70 h-2 rounded-full" style={{ width: `${pct}%` }} /></div><span className="text-xs font-mono text-muted-foreground w-16 text-right">{c.count.toLocaleString()}</span></div>); })}</div></CardContent></Card>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card data-testid="sources-card"><CardHeader className="pb-3"><CardTitle className="text-base">Data Sources</CardTitle></CardHeader><CardContent><div className="space-y-1">{(overview?.sources || []).map((s, i) => (<div key={i} className="flex justify-between text-sm py-1 border-b border-muted/50 last:border-0"><span className="text-muted-foreground">{s.name}</span><span className="font-mono font-medium">{s.count.toLocaleString()}</span></div>))}</div></CardContent></Card>
        <Card data-testid="years-card"><CardHeader className="pb-3"><CardTitle className="text-base">Cases by Year (Recent)</CardTitle></CardHeader><CardContent><div className="flex flex-wrap gap-1.5">{(overview?.years || []).filter(y => y.year).map((y, i) => (<div key={i} className="px-2 py-1 rounded bg-muted/50 text-center min-w-[70px]"><p className="text-xs text-muted-foreground">{y.year}</p><p className="text-xs font-bold font-mono">{y.count.toLocaleString()}</p></div>))}</div></CardContent></Card>
      </div>
    </div>
  );
};

export default MonitorDashboard;
