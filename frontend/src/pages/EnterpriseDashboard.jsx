import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getEnterpriseStats } from '@/services/enterpriseService';

const EnterpriseDashboard = () => {
  const [stats, setStats] = useState({});

  useEffect(() => {
    getEnterpriseStats().then(setStats);
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Enterprise Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="p-4">
          <h3 className="text-lg font-bold">Total Users</h3>
          <p className="text-2xl">{stats.total_users || 0}</p>
        </Card>
        <Card className="p-4">
          <h3 className="text-lg font-bold">Searches</h3>
          <p className="text-2xl">{stats.total_searches || 0}</p>
        </Card>
        <Card className="p-4">
          <h3 className="text-lg font-bold">Cases</h3>
          <p className="text-2xl">{stats.total_cases || 0}</p>
        </Card>
      </div>
      <div className="space-y-3">
        {stats.recent_activity?.map(act => (
          <Card key={act.id} className="p-4">
            <Badge variant="outline">{act.type}</Badge>
            <p className="text-sm">{act.description}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default EnterpriseDashboard;
