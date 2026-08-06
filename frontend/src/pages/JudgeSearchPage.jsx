import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getJudges } from '@/services/judgeService';

const JudgeSearchPage = () => {
  const navigate = useNavigate();
  const [judges, setJudges] = useState([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    getJudges().then(setJudges);
  }, []);

  const filtered = judges.filter(j =>
    j.name.toLowerCase().includes(query.toLowerCase()) ||
    j.court.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Judge Search</h1>
      <div className="flex gap-2 mb-4">
        <Input placeholder="Search judges..." value={query} onChange={(e) => setQuery(e.target.value)} />
        <Button onClick={() => setQuery('')}>Clear</Button>
      </div>
      <div className="space-y-3">
        {filtered.map(judge => (
          <Card key={judge.id} className="p-4 cursor-pointer" onClick={() => navigate(`/judge/${judge.id}`)}>
            <h3 className="font-bold">{judge.name}</h3>
            <Badge variant="outline">{judge.court}</Badge>
            <p className="text-sm text-muted-foreground">{judge.designation}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default JudgeSearchPage;
