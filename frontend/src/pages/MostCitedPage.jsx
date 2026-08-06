import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';

const MostCitedPage = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchMostCitedCases();
  }, []);

  const fetchMostCitedCases = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/cases/most-cited', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch most cited cases');
      }

      const data = await response.json();
      setCases(data.cases || []);
    } catch (error) {
      console.error('Error:', error);
      toast({
        title: 'Error',
        description: 'Failed to load most cited cases',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/4"></div>
          <div className="h-32 bg-muted rounded"></div>
          <div className="h-32 bg-muted rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Most Cited Cases</h1>
      <p className="text-muted-foreground mb-6">
        Cases that are most frequently cited in other judgments
      </p>
      <div className="space-y-4">
        {cases.map((caseItem, index) => (
          <Card key={caseItem.id} className="cursor-pointer hover:bg-accent/50" onClick={() => window.location.href = `/case/${caseItem.id}`}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl font-bold text-muted-foreground">#{index + 1}</span>
                    <h3 className="font-semibold">{caseItem.title}</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">{caseItem.citation}</p>
                  <p className="text-sm text-muted-foreground">{caseItem.court} • {caseItem.year}</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{caseItem.citation_count}</div>
                  <div className="text-xs text-muted-foreground">citations</div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default MostCitedPage;
