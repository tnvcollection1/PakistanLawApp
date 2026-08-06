import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Timeline } from '@/components/ui/timeline';
import { getCaseTimeline } from '@/services/caseService';

const LegalTimelinePage = () => {
  const navigate = useNavigate();
  const [timeline, setTimeline] = useState([]);

  useEffect(() => {
    getCaseTimeline().then(setTimeline);
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Legal Timeline</h1>
      <Timeline>
        {timeline.map((event) => (
          <div key={event.id} className="mb-4">
            <div className="font-bold">{event.date}</div>
            <Card className="p-4 cursor-pointer" onClick={() => navigate(`/case/${event.case_id}`)}>
              <h3 className="font-bold">{event.title}</h3>
              <p className="text-sm text-muted-foreground">{event.description}</p>
            </Card>
          </div>
        ))}
      </Timeline>
    </div>
  );
};

export default LegalTimelinePage;
