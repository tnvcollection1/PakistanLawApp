import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { getDashboardStats } from '@/services/dashboardService';

const DashboardModern = () => {
  const [stats, setStats] = useState({});

  useEffect(() => {
    getDashboardStats().then(setStats);
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="p-4">
          <h3 className="text-lg font-bold">Total Cases</h3>
          <p className="text-2xl">{stats.total_cases || 0}</p>
        </Card>
        <Card className="p-4">
          <h3 className="text-lg font-bold">Total Statutes</h3>
          <p className="text-2xl">{stats.total_statutes || 0}</p>
        </Card>
        <Card className="p-4">
          <h3 className="text-lg font-bold">Total Journals</h3>
          <p className="text-2xl">{stats.total_journals || 0}</p>
        </Card>
        <Card className="p-4">
          <h3 className="text-lg font-bold">Total Users</h3>
          <p className="text-2xl">{stats.total_users || 0}</p>
        </Card>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4">
          <h3 className="text-lg font-bold mb-2">Recent Cases</h3>
          <div className="space-y-2">
            {stats.recent_cases?.map(c => (
              <div key={c.id} className="p-2 border rounded">
                <p className="font-bold">{c.title}</p>
                <p className="text-sm text-muted-foreground">{c.citation}</p>
              </div>
            ))}
          </div>
        </Card>
        <Card className="p-4">
          <h3 className="text-lg font-bold mb-2">Top Searches</h3>
          <div className="space-y-2">
            {stats.top_searches?.map(s => (
              <div key={s.query} className="p-2 border rounded">
                <p>{s.query}</p>
                <p className="text-sm text-muted-foreground">{s.count} searches</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default DashboardModern;
