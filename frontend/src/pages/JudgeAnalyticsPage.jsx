import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Gavel, TrendingUp, Building, Calendar, ChevronRight, Loader2, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { PageTransition, FadeInUp, StaggerContainer, StaggerItem } from '../components/Animations';
import SidebarLayout from '../components/SidebarLayout';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';

const API = process.env.REACT_APP_BACKEND_URL || '';
const COLORS = ['#1e3a8a', '#3b82f6', '#0891b2', '#059669', '#6366f1', '#8b5cf6', '#14b8a6', '#0284c7'];

export default function JudgeAnalyticsPage() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedJudge, setSelectedJudge] = useState(null);
  const [judgeDetail, setJudgeDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => { fetchDashboard(); }, []);

  const fetchDashboard = async () => {
    try {
      const res = await fetch(`${API}/api/analytics/judges-dashboard`);
      if (res.ok) setData(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const selectJudge = async (judgeName) => {
    setSelectedJudge(judgeName);
    setDetailLoading(true);
    try {
      const res = await fetch(`${API}/api/analytics/judge/${encodeURIComponent(judgeName)}`);
      if (res.ok) setJudgeDetail(await res.json());
    } catch (e) { console.error(e); }
    finally { setDetailLoading(false); }
  };

  const filteredJudges = data?.judges?.filter(j =>
    !searchTerm || j.name.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-background border border-muted dark:border-border rounded-lg p-3 shadow-lg">
          <p className="text-sm font-medium text-slate-900 dark:text-primary-foreground">{label || payload[0]?.payload?.name}</p>
          <p className="text-sm text-primary dark:text-primary font-mono">{payload[0]?.value?.toLocaleString()} cases</p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <SidebarLayout>
        <div className="min-h-screen bg-background dark:bg-background flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      </SidebarLayout>
    );
  }

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background dark:bg-background" data-testid="judge-analytics-page">
        {/* Page Header */}
        <div className="bg-white dark:bg-background border-b border-muted dark:border-border px-6 md:px-10 py-6">
          <div className="max-w-screen-2xl mx-auto">
            <FadeInUp>
              <h1 className="font-serif text-2xl md:text-3xl font-bold text-slate-900 dark:text-primary-foreground flex items-center gap-3" data-testid="judge-analytics-title">
                <Gavel size={24} className="text-primary" />
                Judge Analytics
              </h1>
              <p className="text-sm md:text-base text-muted-foreground dark:text-muted-foreground mt-2 leading-relaxed">
                Ruling patterns and case distribution across {data?.total_judges_count?.toLocaleString() || 0} judges
              </p>
            </FadeInUp>
          </div>
        </div>

        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-8">
          {/* Top Judges Bar Chart */}
          <Card className="mb-8 border-muted dark:border-border" data-testid="top-judges-chart">
            <CardHeader className="pb-2">
              <CardTitle className="font-serif text-lg md:text-xl text-slate-900 dark:text-primary-foreground">Top 15 Judges by Case Count</CardTitle>
            </CardHeader>
            <CardContent className="overflow-x-auto pt-4">
              <div className="min-w-[600px]">
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={filteredJudges.slice(0, 15)} layout="vertical" margin={{ left: 200, right: 20, top: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.5} horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 13, fill: '#64748b' }} width={190} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="total_cases" fill="#f59e0b" radius={[0, 6, 6, 0]} cursor="pointer"
                      onClick={(d) => selectJudge(d.name)} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Judge List */}
            <div className="lg:col-span-1">
              <Card className="border-muted dark:border-border" data-testid="judges-list">
                <CardHeader className="pb-3">
                  <CardTitle className="font-serif text-lg text-slate-900 dark:text-primary-foreground">All Judges</CardTitle>
                  <div className="relative mt-3">
                    <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Search judges..."
                      className="w-full pl-10 pr-4 py-2.5 border border-muted dark:border-border rounded-xl text-sm bg-white dark:bg-card text-slate-900 dark:text-primary-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary placeholder:text-muted-foreground"
                      data-testid="judge-search-input"
                    />
                  </div>
                </CardHeader>
                <CardContent className="max-h-[560px] overflow-y-auto p-0">
                  {filteredJudges.map((j, i) => (
                    <button
                      key={j.name}
                      onClick={() => selectJudge(j.name)}
                      data-testid={`judge-item-${i}`}
                      className={`w-full text-left px-5 py-4 border-b border-slate-100 dark:border-border hover:bg-background dark:hover:bg-card/50 transition-colors duration-200 flex items-center justify-between ${
                        selectedJudge === j.name ? 'bg-primary/10/50 dark:bg-primary/10 border-l-3 border-l-primary/100' : ''
                      }`}
                    >
                      <div>
                        <p className="font-medium text-sm text-slate-900 dark:text-primary-foreground">{j.name}</p>
                        <div className="flex gap-2 mt-1.5">
                          <Badge variant="outline" className="text-xs font-mono">{j.total_cases} cases</Badge>
                          {j.active_years > 0 && (
                            <Badge variant="outline" className="text-xs text-muted-foreground dark:text-muted-foreground">
                              {j.first_year}-{j.last_year}
                            </Badge>
                          )}
                        </div>
                      </div>
                      <ChevronRight size={14} className="text-muted-foreground dark:text-foreground" />
                    </button>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Judge Detail */}
            <div className="lg:col-span-2">
              {detailLoading ? (
                <Card className="border-muted dark:border-border">
                  <CardContent className="flex items-center justify-center py-24">
                    <Loader2 className="w-8 h-8 animate-spin text-primary" />
                  </CardContent>
                </Card>
              ) : judgeDetail ? (
                <div className="space-y-6">
                  {/* Stats */}
                  <Card className="border-muted dark:border-border" data-testid="judge-detail-card">
                    <CardHeader className="pb-2">
                      <CardTitle className="font-serif text-xl text-slate-900 dark:text-primary-foreground flex items-center gap-3">
                        <Gavel size={20} className="text-primary" />
                        {judgeDetail.judge}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-4">
                      <div className="grid grid-cols-3 gap-4 mb-8">
                        <div className="bg-primary/10 dark:bg-primary/20 rounded-xl p-5 text-center border border-primary/20 dark:border-primary/30">
                          <p className="text-3xl font-bold text-slate-900 dark:text-primary-foreground font-mono">{judgeDetail.total_cases.toLocaleString()}</p>
                          <p className="text-xs text-primary dark:text-primary mt-1.5 font-semibold uppercase tracking-wide">Total Cases</p>
                        </div>
                        <div className="bg-background dark:bg-card rounded-xl p-5 text-center border border-muted dark:border-border">
                          <p className="text-3xl font-bold text-slate-900 dark:text-primary-foreground font-mono">{judgeDetail.active_years}</p>
                          <p className="text-xs text-muted-foreground dark:text-muted-foreground mt-1.5 font-semibold uppercase tracking-wide">Active Years</p>
                        </div>
                        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-5 text-center border border-blue-100 dark:border-blue-800/30">
                          <p className="text-3xl font-bold text-slate-900 dark:text-primary-foreground font-mono">{judgeDetail.courts?.length || 0}</p>
                          <p className="text-xs text-blue-700 dark:text-blue-400 mt-1.5 font-semibold uppercase tracking-wide">Courts</p>
                        </div>
                      </div>

                      {/* Cases Over Time */}
                      {judgeDetail.years?.length > 0 && (
                        <div>
                          <p className="text-sm font-semibold text-foreground dark:text-muted-foreground mb-4 uppercase tracking-wide">Cases Over Time</p>
                          <ResponsiveContainer width="100%" height={220}>
                            <LineChart data={judgeDetail.years}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.5} />
                              <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                              <Tooltip content={<CustomTooltip />} />
                              <Line type="monotone" dataKey="count" stroke="#f59e0b" strokeWidth={2.5} dot={{ r: 3, fill: '#f59e0b' }} activeDot={{ r: 5 }} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Court Distribution */}
                  {judgeDetail.courts?.length > 0 && (
                    <Card className="border-muted dark:border-border" data-testid="judge-courts-card">
                      <CardHeader><CardTitle className="font-serif text-lg text-slate-900 dark:text-primary-foreground">Court Distribution</CardTitle></CardHeader>
                      <CardContent>
                        <ResponsiveContainer width="100%" height={260}>
                          <PieChart>
                            <Pie data={judgeDetail.courts} dataKey="count" nameKey="name" cx="50%" cy="50%"
                              outerRadius={100} innerRadius={50} label={({ name, percent }) => `${name.split(' ')[0]} ${(percent * 100).toFixed(0)}%`}>
                              {judgeDetail.courts.map((_, i) => (
                                <Cell key={i} fill={COLORS[i % COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip content={<CustomTooltip />} />
                          </PieChart>
                        </ResponsiveContainer>
                      </CardContent>
                    </Card>
                  )}

                  {/* Recent Cases */}
                  {judgeDetail.recent_cases?.length > 0 && (
                    <Card className="border-muted dark:border-border" data-testid="judge-recent-cases">
                      <CardHeader><CardTitle className="font-serif text-lg text-slate-900 dark:text-primary-foreground">Recent Cases</CardTitle></CardHeader>
                      <CardContent className="p-0">
                        {judgeDetail.recent_cases.slice(0, 10).map((c, i) => (
                          <button
                            key={c.case_id}
                            onClick={() => navigate(`/case/${c.case_id}`)}
                            className="w-full text-left px-5 py-3.5 border-b border-slate-100 dark:border-border hover:bg-background dark:hover:bg-card/50 transition-colors duration-200 flex items-center justify-between"
                            data-testid={`judge-case-${i}`}
                          >
                            <div>
                              <p className="text-sm font-mono font-medium text-primary dark:text-primary">{c.case_id}</p>
                              <p className="text-xs text-muted-foreground dark:text-muted-foreground truncate max-w-md mt-0.5">{c.parties}</p>
                            </div>
                            <Badge variant="outline" className="text-xs font-mono">{c.year}</Badge>
                          </button>
                        ))}
                      </CardContent>
                    </Card>
                  )}
                </div>
              ) : (
                <Card className="border-muted dark:border-border">
                  <CardContent className="flex flex-col items-center justify-center py-24 text-center">
                    <div className="w-16 h-16 rounded-2xl bg-muted dark:bg-card flex items-center justify-center mb-4">
                      <Gavel size={28} className="text-muted-foreground dark:text-foreground" />
                    </div>
                    <p className="text-muted-foreground dark:text-muted-foreground text-base">Select a judge from the list to view detailed analytics</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
}
