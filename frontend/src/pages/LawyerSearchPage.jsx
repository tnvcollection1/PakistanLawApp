import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getLawyers } from '@/services/lawyerService';

const LawyerSearchPage = () => {
  const navigate = useNavigate();
  const [lawyers, setLawyers] = useState([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    getLawyers().then(setLawyers);
  }, []);

  const filtered = lawyers.filter(l =>
    l.name.toLowerCase().includes(query.toLowerCase()) ||
    l.firm?.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Lawyer Search</h1>
      <div className="flex gap-2 mb-4">
        <Input placeholder="Search lawyers..." value={query} onChange={(e) => setQuery(e.target.value)} />
        <Button onClick={() => setQuery('')}>Clear</Button>
      </div>
      <div className="space-y-3">
        {filtered.map(lawyer => (
          <Card key={lawyer.id} className="p-4 cursor-pointer" onClick={() => navigate(`/lawyer/${lawyer.id}`)}>
            <h3 className="font-bold">{lawyer.name}</h3>
            <Badge variant="outline">{lawyer.firm}</Badge>
            <p className="text-sm text-muted-foreground">{lawyer.specialization}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default LawyerSearchPage;
