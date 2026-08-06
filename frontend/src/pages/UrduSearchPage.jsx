import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs } from '@/components/ui/tabs';
import { AILoader } from '@/components/AILoader';
import { searchCasesAI } from '@/services/aiSearch';

const UrduSearchPage = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    const data = await searchCasesAI(query, { urdu: true });
    setResults(data);
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Urdu Search</h1>
      <div className="flex gap-2 mb-6">
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search in Urdu..." />
        <Button onClick={handleSearch} className="bg-primary">Search</Button>
      </div>
      {loading && <AILoader />}
      <div className="space-y-4">
        {results.map((c) => (
          <Card key={c.id} className="p-4 cursor-pointer" onClick={() => navigate(`/case/${c.id}`)}>
            <h3 className="font-bold">{c.title_urdu || c.title}</h3>
            <Badge variant="outline">{c.court}</Badge>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default UrduSearchPage;