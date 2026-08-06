import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { scanNewCases } from '@/services/scannerService';

const ScannerPage = () => {
  const [results, setResults] = useState([]);
  const [scanning, setScanning] = useState(false);

  const handleScan = async () => {
    setScanning(true);
    const data = await scanNewCases();
    setResults(data);
    setScanning(false);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">New Cases Scanner</h1>
      <Button onClick={handleScan} disabled={scanning} className="mb-4">
        {scanning ? 'Scanning...' : 'Scan Now'}
      </Button>
      <div className="space-y-3">
        {results.map(res => (
          <Card key={res.id} className="p-4">
            <h3 className="font-bold">{res.title}</h3>
            <p className="text-sm text-muted-foreground">{res.citation}</p>
            <Badge variant={res.is_new ? 'default' : 'outline'}>
              {res.is_new ? 'New' : 'Existing'}
            </Badge>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ScannerPage;
