import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { getCalendarEvents } from '@/services/calendarService';

const EnterpriseCalendar = () => {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    getCalendarEvents().then(setEvents);
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Enterprise Calendar</h1>
      <div className="grid grid-cols-7 gap-2 mb-4">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => (
          <div key={d} className="text-center font-bold">{d}</div>
        ))}
      </div>
      <div className="space-y-3">
        {events.map(event => (
          <Card key={event.id} className="p-4">
            <div className="flex justify-between items-center">
              <h3 className="font-bold">{event.title}</h3>
              <span className="text-sm text-muted-foreground">{event.date}</span>
            </div>
            <p className="text-sm text-muted-foreground">{event.description}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default EnterpriseCalendar;
