import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getSmartCase } from '@/services/caseService';

const SmartCaseReader = ({ caseId }) => {
  const [caseData, setCaseData] = useState(null);
  const [highlighted, setHighlighted] = useState([]);

  useEffect(() => {
    getSmartCase(caseId).then(data => {
      setCaseData(data);
      setHighlighted(data.key_passages || []);
    });
  }, [caseId]);

  if (!caseData) return <p>Loading...</p>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-2">{caseData.title}</h1>
      <div className="flex gap-2 mb-4">
        <Badge variant="outline">{caseData.citation}</Badge>
        <Badge variant="outline">{caseData.court}</Badge>
        <Badge variant="outline">{caseData.date}</Badge>
      </div>
      <div className="space-y-2">
        {caseData.paragraphs?.map((p, i) => (
          <p key={i} className={highlighted.includes(i) ? 'bg-yellow-100 dark:bg-yellow-900' : ''}>
            {p}
          </p>
        ))}
      </div>
    </div>
  );
};

export default SmartCaseReader;
