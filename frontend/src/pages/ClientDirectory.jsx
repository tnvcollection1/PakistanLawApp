import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getClients } from '@/services/clientService';

const ClientDirectory = () => {
  const [clients, setClients] = useState([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    getClients().then(setClients);
  }, []);

  const filtered = clients.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Client Directory</h1>
      <div className="flex gap-2 mb-4">
        <Input placeholder="Search clients..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <Button onClick={() => setSearch('')}>Clear</Button>
      </div>
      <div className="space-y-3">
        {filtered.map(client => (
          <Card key={client.id} className="p-4">
            <div className="flex justify-between items-center">
              <h3 className="font-bold">{client.name}</h3>
              <Badge variant="outline">{client.type}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{client.email}</p>
            <p className="text-sm text-muted-foreground">{client.phone}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ClientDirectory;
