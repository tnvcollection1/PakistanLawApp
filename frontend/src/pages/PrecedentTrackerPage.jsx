import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { getPrecedents } from '@/services/caseService';

const PrecedentTrackerPage = () => {
  const navigate = useNavigate();
  const [precedents, setPrecedents] = useState([]);
  const [filter, setFilter] = useState('');
  const [status, setStatus] = useState('all');

  useEffect(() => {
    getPrecedents().then(setPrecedents);
  }, []);

  const filtered = precedents.filter(p => {
    const matchFilter = p.title.toLowerCase().includes(filter.toLowerCase()) ||
                        p.citation.toLowerCase().includes(filter.toLowerCase());
    const matchStatus = status === 'all' || p.status === status;
    return matchFilter && matchStatus;
  });

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Precedent Tracker</h1>
      <div className="flex gap-2 mb-4">
        <Input placeholder="Filter by title or citation..." value={filter} onChange={(e) => setFilter(e.target.value)} />
        <Tabs value={status} onValueChange={setStatus}>
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="good">Good Law</TabsTrigger>
            <TabsTrigger value="questioned">Questioned</TabsTrigger>
            <TabsTrigger value="overruled">Overruled</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
      <div className="space-y-3">
        {filtered.map(p => (
          <Card key={p.id} className="p-4 cursor-pointer" onClick={() => navigate(`/case/${p.case_id}`)}>
            <div className="flex justify-between items-center">
              <h3 className="font-bold">{p.title}</h3>
              <Badge variant={p.status === 'good' ? 'default' : p.status === 'overruled' ? 'destructive' : 'outline'}>
                {p.status}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">{p.citation}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default PrecedentTrackerPage;
