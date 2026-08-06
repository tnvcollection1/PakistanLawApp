import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getJudgeInsights } from '@/services/judgeService';

const JudgeInsightsPage = () => {
  const [judge, setJudge] = useState(null);

  useEffect(() => {
    getJudgeInsights().then(setJudge);
  }, []);

  if (!judge) return <p>Loading...</p>;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Judge Insights</h1>
      <Card className="p-6 mb-4">
        <h2 className="text-2xl font-bold">{judge.name}</h2>
        <Badge variant="outline" className="mb-2">{judge.court}</Badge>
        <p className="text-muted-foreground">{judge.designation}</p>
      </Card>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <Card className="p-4">
          <h3 className="text-lg font-bold">Total Cases</h3>
          <p className="text-2xl">{judge.total_cases || 0}</p>
        </Card>
        <Card className="p-4">
          <h3 className="text-lg font-bold">Decisions</h3>
          <p className="text-2xl">{judge.decisions || 0}</p>
        </Card>
        <Card className="p-4">
          <h3 className="text-lg font-bold">Dissent Rate</h3>
          <p className="text-2xl">{judge.dissent_rate || 0}%</p>
        </Card>
      </div>
      <h2 className="text-xl font-bold mb-2">Recent Cases</h2>
      <div className="space-y-3">
        {judge.recent_cases?.map(c => (
          <Card key={c.id} className="p-4">
            <h3 className="font-bold">{c.title}</h3>
            <p className="text-sm text-muted-foreground">{c.citation}</p>
            <Badge variant={c.decision === 'allowed' ? 'default' : 'destructive'}>
              {c.decision}
            </Badge>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default JudgeInsightsPage;
