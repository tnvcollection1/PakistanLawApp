import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getWhatsNew } from '@/services/whatsNewService';

const WhatsNewPage = () => {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);

  useEffect(() => {
    getWhatsNew().then(setItems);
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">What's New</h1>
      <div className="space-y-3">
        {items.map(item => (
          <Card key={item.id} className="p-4 cursor-pointer" onClick={() => navigate(item.link)}>
            <div className="flex justify-between items-center">
              <h3 className="font-bold">{item.title}</h3>
              <Badge variant="outline">{item.type}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{item.description}</p>
            <p className="text-xs text-muted-foreground">{item.date}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default WhatsNewPage;
