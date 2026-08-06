import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getPartyCases } from '@/services/caseService';

const PartySearchPage = () => {
  const navigate = useNavigate();
  const [party, setParty] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!party.trim()) return;
    setLoading(true);
    const data = await getPartyCases(party);
    setResults(data);
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Party Search</h1>
      <div className="flex gap-2 mb-4">
        <Input value={party} onChange={(e) => setParty(e.target.value)} placeholder="Enter party name..." />
        <Button onClick={handleSearch} className="bg-primary">Search</Button>
      </div>
      {loading && <p className="text-muted-foreground">Loading...</p>}
      <div className="space-y-3">
        {results.map(c => (
          <Card key={c.id} className="p-4 cursor-pointer" onClick={() => navigate(`/case/${c.id}`)}>
            <h3 className="font-bold">{c.title}</h3>
            <p className="text-sm text-muted-foreground">{c.citation}</p>
            <Badge variant="outline">{c.court}</Badge>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default PartySearchPage;
