import React, { useState, useEffect } from 'react';
import { useToast } from '@/hooks/use-toast';

const RelatedCasesPanel = ({ caseId, currentCase }) => {
  const [relatedCases, setRelatedCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    if (caseId) {
      fetchRelatedCases();
    }
  }, [caseId]);

  const fetchRelatedCases = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/cases/${caseId}/related`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch related cases');
      }

      const data = await response.json();
      setRelatedCases(data.related_cases || []);
    } catch (error) {
      console.error('Error fetching related cases:', error);
      toast({
        title: 'Error',
        description: 'Failed to load related cases',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-muted rounded w-3/4"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
          <div className="h-4 bg-muted rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (relatedCases.length === 0) {
    return (
      <div className="p-4 text-center text-muted-foreground">
        No related cases found
      </div>
    );
  }

  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4">Related Cases</h3>
      <div className="space-y-3">
        {relatedCases.map((relatedCase) => (
          <div
            key={relatedCase.id}
            className="p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors cursor-pointer"
            onClick={() => window.open(`/case/${relatedCase.id}`, '_blank')}
          >
            <div className="font-medium text-sm">{relatedCase.title}</div>
            <div className="text-xs text-muted-foreground mt-1">
              {relatedCase.citation} • {relatedCase.court} • {relatedCase.year}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Similarity: {Math.round(relatedCase.similarity_score * 100)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RelatedCasesPanel;
