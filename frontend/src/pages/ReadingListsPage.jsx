import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { getReadingLists, createReadingList } from '@/services/readingListService';

const ReadingListsPage = () => {
  const navigate = useNavigate();
  const [lists, setLists] = useState([]);
  const [newList, setNewList] = useState('');

  useEffect(() => {
    getReadingLists().then(setLists);
  }, []);

  const handleCreate = async () => {
    if (!newList.trim()) return;
    const created = await createReadingList(newList);
    setLists([...lists, created]);
    setNewList('');
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Reading Lists</h1>
      <div className="flex gap-2 mb-4">
        <Input placeholder="New list name..." value={newList} onChange={(e) => setNewList(e.target.value)} />
        <Button onClick={handleCreate}>Create</Button>
      </div>
      <div className="space-y-3">
        {lists.map(list => (
          <Card key={list.id} className="p-4 cursor-pointer" onClick={() => navigate(`/reading-list/${list.id}`)}>
            <div className="flex justify-between items-center">
              <h3 className="font-bold">{list.name}</h3>
              <Badge variant="outline">{list.count} cases</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{list.description}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ReadingListsPage;
