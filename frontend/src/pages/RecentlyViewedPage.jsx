import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getRecentlyViewed } from '@/services/historyService';

const RecentlyViewedPage = () => {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);

  useEffect(() => {
    getRecentlyViewed().then(setCases);
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Recently Viewed</h1>
      <div className="space-y-3">
        {cases.map(c => (
          <Card key={c.id} className="p-4 cursor-pointer" onClick={() => navigate(`/case/${c.id}`)}>
            <h3 className="font-bold">{c.title}</h3>
            <p className="text-sm text-muted-foreground">{c.citation}</p>
            <Badge variant="outline">{c.court}</Badge>
            <p className="text-xs text-muted-foreground">Viewed: {c.viewed_at}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default RecentlyViewedPage;
