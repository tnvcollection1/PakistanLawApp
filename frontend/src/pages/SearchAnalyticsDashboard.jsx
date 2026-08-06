import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { getSearchAnalytics } from '@/services/analyticsService';

const SearchAnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState({});

  useEffect(() => {
    getSearchAnalytics().then(setAnalytics);
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Search Analytics</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="p-4">
          <h3 className="text-lg font-bold">Total Searches</h3>
          <p className="text-2xl">{analytics.total_searches || 0}</p>
        </Card>
        <Card className="p-4">
          <h3 className="text-lg font-bold">Unique Users</h3>
          <p className="text-2xl">{analytics.unique_users || 0}</p>
        </Card>
        <Card className="p-4">
          <h3 className="text-lg font-bold">Avg Results</h3>
          <p className="text-2xl">{analytics.avg_results || 0}</p>
        </Card>
      </div>
      <h2 className="text-xl font-bold mb-2">Top Queries</h2>
      <div className="space-y-2">
        {analytics.top_queries?.map(q => (
          <Card key={q.query} className="p-3">
            <div className="flex justify-between">
              <span>{q.query}</span>
              <span className="text-muted-foreground">{q.count} searches</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default SearchAnalyticsDashboard;
