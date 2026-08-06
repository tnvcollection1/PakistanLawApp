import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getMaxims } from '@/services/maximService';

const MaximsPage = () => {
  const navigate = useNavigate();
  const [maxims, setMaxims] = useState([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    getMaxims().then(setMaxims);
  }, []);

  const filtered = maxims.filter(m =>
    m.latin.toLowerCase().includes(query.toLowerCase()) ||
    m.translation.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Legal Maxims</h1>
      <div className="flex gap-2 mb-4">
        <Input placeholder="Search maxims..." value={query} onChange={(e) => setQuery(e.target.value)} />
        <Button onClick={() => setQuery('')}>Clear</Button>
      </div>
      <div className="space-y-3">
        {filtered.map(maxim => (
          <Card key={maxim.id} className="p-4">
            <h3 className="font-bold italic">{maxim.latin}</h3>
            <p className="text-sm text-muted-foreground">{maxim.translation}</p>
            <Badge variant="outline">{maxim.category}</Badge>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default MaximsPage;
