import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, Legend
} from 'recharts';
import {
  Scale, Gavel, Building, Loader2, ArrowLeftRight, TrendingUp,
  ChevronDown, Database, FileText, Users
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '../components/ui/select';
import SidebarLayout from '../components/SidebarLayout';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const COURT_LIST = [
  'Lahore High Court', 'Sindh High Court', 'Supreme Court',
  'Peshawar High Court', 'Balochistan High Court', 'Islamabad High Court',
  'Federal Shariat Court', 'Service Tribunal', 'Appellate Tribunal',
  'Income Tax Tribunal', 'Supreme Court AJK', 'High Court AJK',
];

const CourtComparison = () => {
  const [court1, setCourt1] = useState('Lahore High Court');
  const [court2, setCourt2] = useState('Sindh High Court');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { compare(); }, []);

  const compare = async () => {
    if (!court1 || !court2) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/analytics/compare-courts?court1=${encodeURIComponent(court1)}&court2=${encodeURIComponent(court2)}`);
      setData(await res.json());
    } catch (e) {
      console.error('Compare error:', e);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ label, val1, val2, icon: Icon, format }) => {
    const fmt = (v) => format === 'pct' ? `${v}%` : v.toLocaleString();
    const diff = val1 - val2;
    return (
      <div className="flex items-center gap-3 p-3 bg-background rounded-lg">
        <Icon size={18} className="text-muted-foreground flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-xs text-muted-foreground dark:text-muted-foreground">{label}</p>
          <div className="flex items-center gap-3 mt-1">
            <span className="font-bold text-primary dark:text-primary">{fmt(val1)}</span>
            <span className="text-xs text-muted-foreground">vs</span>
            <span className="font-bold text-blue-700">{fmt(val2)}</span>
            {diff !== 0 && (
              <span className={`text-xs px-1.5 py-0.5 rounded ${diff > 0 ? 'bg-emerald-100 text-primary dark:text-primary' : 'bg-blue-100 text-blue-700'}`}>
                {diff > 0 ? '+' : ''}{fmt(Math.abs(diff))}
              </span>
            )}
          </div>
        </div>
      </div>
    );
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-background px-3 py-2 border rounded shadow-lg text-sm">
          <p className="font-medium mb-1">{label}</p>
          {payload.map((p, i) => (
            <p key={i} style={{ color: p.color }}>{p.name}: {p.value.toLocaleString()}</p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background dark:bg-background">
        {/* Header */}
        <div className="bg-white dark:bg-background border-b border-muted dark:border-border shadow-sm">
          <div className="max-w-6xl mx-auto px-6 py-6">
            <div className="flex items-center gap-3">
              <ArrowLeftRight className="text-emerald-600" size={24} />
              <div>
                <h1 className="text-2xl font-serif font-bold text-emerald-900" data-testid="compare-title">Court Comparison</h1>
                <p className="text-muted-foreground dark:text-muted-foreground text-sm mt-0.5">Side-by-side analysis of case volume, trends, and judges</p>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto px-6 py-6 space-y-6">
          {/* Court Selection */}
          <Card>
            <CardContent className="p-5">
              <div className="flex items-center gap-4 flex-wrap">
                <div className="flex-1 min-w-[200px]">
                  <label className="text-sm font-medium text-primary dark:text-primary mb-1 block">Court 1</label>
                  <Select value={court1} onValueChange={setCourt1}>
                    <SelectTrigger data-testid="court1-select" className="border-emerald-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {COURT_LIST.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end pb-1">
                  <ArrowLeftRight size={20} className="text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-[200px]">
                  <label className="text-sm font-medium text-blue-700 mb-1 block">Court 2</label>
                  <Select value={court2} onValueChange={setCourt2}>
                    <SelectTrigger data-testid="court2-select" className="border-blue-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {COURT_LIST.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end">
                  <Button onClick={compare} className="bg-emerald-600 hover:bg-emerald-700" disabled={loading || court1 === court2} data-testid="compare-btn">
                    {loading ? <Loader2 size={16} className="animate-spin mr-1" /> : <Scale size={16} className="mr-1" />}
                    Compare
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {loading && (
            <div className="flex justify-center py-16"><Loader2 className="w-10 h-10 animate-spin text-primary" /></div>
          )}

          {data && !loading && (
            <>
              {/* Stats Comparison */}
              <div className="grid md:grid-cols-2 gap-6">
                <Card className="border-l-4 border-l-emerald-500" data-testid="court1-stats">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg text-emerald-800">
                      <Building size={18} className="inline mr-2" />{data.court1.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <StatCard label="Total Cases" val1={data.court1.total} val2={data.court2.total} icon={Database} />
                    <StatCard label="With Full Text" val1={data.court1.with_content} val2={data.court2.with_content} icon={FileText} />
                    <StatCard label="Content Coverage" val1={data.court1.total ? Math.round(data.court1.with_content / data.court1.total * 100) : 0} val2={data.court2.total ? Math.round(data.court2.with_content / data.court2.total * 100) : 0} icon={TrendingUp} format="pct" />
                  </CardContent>
                </Card>
                <Card className="border-l-4 border-l-blue-500" data-testid="court2-stats">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg text-blue-800">
                      <Building size={18} className="inline mr-2" />{data.court2.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <StatCard label="Total Cases" val1={data.court2.total} val2={data.court1.total} icon={Database} />
                    <StatCard label="With Full Text" val1={data.court2.with_content} val2={data.court1.with_content} icon={FileText} />
                    <StatCard label="Content Coverage" val1={data.court2.total ? Math.round(data.court2.with_content / data.court2.total * 100) : 0} val2={data.court1.total ? Math.round(data.court1.with_content / data.court1.total * 100) : 0} icon={TrendingUp} format="pct" />
                  </CardContent>
                </Card>
              </div>

              {/* Year Trend Comparison */}
              <Card data-testid="year-comparison-chart">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <TrendingUp size={18} className="text-emerald-600" /> Year-by-Year Comparison
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={350}>
                    <AreaChart data={data.merged_years} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                      <defs>
                        <linearGradient id="cg1" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#047857" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#047857" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="cg2" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                      <YAxis tickFormatter={(v) => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Area type="monotone" dataKey="court1" name={data.court1.name} stroke="#047857" strokeWidth={2} fill="url(#cg1)" />
                      <Area type="monotone" dataKey="court2" name={data.court2.name} stroke="#2563eb" strokeWidth={2} fill="url(#cg2)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Top Judges Side by Side */}
              <div className="grid md:grid-cols-2 gap-6">
                <Card data-testid="court1-judges">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg text-emerald-800">
                      <Gavel size={18} /> Top Judges — {data.court1.name.split(' ')[0]}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {data.court1.judges.length > 0 ? (
                      <div className="space-y-2.5">
                        {data.court1.judges.map((j, i) => {
                          const max = data.court1.judges[0]?.count || 1;
                          return (
                            <div key={i}>
                              <div className="flex justify-between text-sm mb-0.5">
                                <span className="text-muted-foreground dark:text-muted-foreground truncate mr-2">{j.name}</span>
                                <span className="text-muted-foreground dark:text-muted-foreground flex-shrink-0">{j.count}</span>
                              </div>
                              <div className="w-full bg-muted rounded-full h-1.5">
                                <div className="h-1.5 rounded-full bg-emerald-500" style={{ width: `${(j.count / max) * 100}%` }} />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">No judge data available</p>
                    )}
                  </CardContent>
                </Card>
                <Card data-testid="court2-judges">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg text-blue-800">
                      <Gavel size={18} /> Top Judges — {data.court2.name.split(' ')[0]}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {data.court2.judges.length > 0 ? (
                      <div className="space-y-2.5">
                        {data.court2.judges.map((j, i) => {
                          const max = data.court2.judges[0]?.count || 1;
                          return (
                            <div key={i}>
                              <div className="flex justify-between text-sm mb-0.5">
                                <span className="text-muted-foreground dark:text-muted-foreground truncate mr-2">{j.name}</span>
                                <span className="text-muted-foreground dark:text-muted-foreground flex-shrink-0">{j.count}</span>
                              </div>
                              <div className="w-full bg-muted rounded-full h-1.5">
                                <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${(j.count / max) * 100}%` }} />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">No judge data available</p>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Decade Comparison Bar Chart */}
              <Card data-testid="decade-comparison-chart">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Scale size={18} className="text-emerald-600" /> Decade Comparison
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {(() => {
                    const allDecades = [...new Set([...data.court1.decades.map(d => d.decade), ...data.court2.decades.map(d => d.decade)])].sort();
                    const d1Map = Object.fromEntries(data.court1.decades.map(d => [d.decade, d.count]));
                    const d2Map = Object.fromEntries(data.court2.decades.map(d => [d.decade, d.count]));
                    const merged = allDecades.map(d => ({ decade: `${d}s`, court1: d1Map[d] || 0, court2: d2Map[d] || 0 }));
                    return (
                      <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={merged}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis dataKey="decade" />
                          <YAxis tickFormatter={(v) => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
                          <Tooltip content={<CustomTooltip />} />
                          <Legend />
                          <Bar dataKey="court1" name={data.court1.name} fill="#047857" radius={[4, 4, 0, 0]} />
                          <Bar dataKey="court2" name={data.court2.name} fill="#2563eb" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    );
                  })()}
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </SidebarLayout>
  );
};

export default CourtComparison;
