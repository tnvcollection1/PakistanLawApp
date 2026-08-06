import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getWordsPhrases } from '@/services/caseService';

const WordsPhrasesPage = () => {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    getWordsPhrases().then(setItems);
  }, []);

  const filtered = items.filter(w =>
    w.phrase.toLowerCase().includes(query.toLowerCase()) ||
    w.meaning.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Words and Phrases</h1>
      <div className="flex gap-2 mb-4">
        <Input placeholder="Search words and phrases..." value={query} onChange={(e) => setQuery(e.target.value)} />
        <Button onClick={() => setQuery('')}>Clear</Button>
      </div>
      <div className="space-y-3">
        {filtered.map(item => (
          <Card key={item.id} className="p-4">
            <h3 className="font-bold">{item.phrase}</h3>
            <p className="text-sm text-muted-foreground">{item.meaning}</p>
            <Badge variant="outline">{item.source}</Badge>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default WordsPhrasesPage;
