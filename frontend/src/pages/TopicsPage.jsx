import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getTopics } from '@/services/topicService';

const TopicsPage = () => {
  const navigate = useNavigate();
  const [topics, setTopics] = useState([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    getTopics().then(setTopics);
  }, []);

  const filtered = topics.filter(t =>
    t.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Topics</h1>
      <div className="flex gap-2 mb-4">
        <Input placeholder="Search topics..." value={query} onChange={(e) => setQuery(e.target.value)} />
        <Button onClick={() => setQuery('')}>Clear</Button>
      </div>
      <div className="flex flex-wrap gap-2">
        {filtered.map(topic => (
          <Badge key={topic.id} className="cursor-pointer text-lg p-2" onClick={() => navigate(`/topic/${topic.id}`)}>
            {topic.name}
          </Badge>
        ))}
      </div>
    </div>
  );
};

export default TopicsPage;
