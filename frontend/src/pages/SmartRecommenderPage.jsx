import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getRecommendations } from '@/services/recommendationService';

const SmartRecommenderPage = () => {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    getRecommendations().then(setRecommendations);
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Smart Recommender</h1>
      <div className="space-y-3">
        {recommendations.map(rec => (
          <Card key={rec.id} className="p-4 cursor-pointer" onClick={() => navigate(`/case/${rec.case_id}`)}>
            <div className="flex justify-between items-center">
              <h3 className="font-bold">{rec.title}</h3>
              <Badge variant="outline">{rec.score}% match</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{rec.reason}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default SmartRecommenderPage;
