import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import SidebarLayout from '../components/SidebarLayout';
import { Zap, Calendar, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function WhatsNewPage() {
  const [updates, setUpdates] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUpdates();
  }, []);

  const fetchUpdates = async () => {
    try {
      const res = await fetch(`${API}/api/whats-new`);
      if (res.ok) {
        const data = await res.json();
        setUpdates(data.updates || []);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background">
        <div className="bg-white dark:bg-background border-b shadow-sm px-4 sm:px-6 py-4 sm:py-5">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-lg sm:text-xl font-semibold text-slate-800 dark:text-foreground flex items-center gap-2">
              <Zap size={20} className="text-yellow-500" /> What&apos;s New
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-1">Latest updates and new case additions</p>
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4 sm:py-8 space-y-4">
          {loading ? (
            <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" /></div>
          ) : updates.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                <Calendar size={40} className="text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium text-foreground mb-2">No updates yet</h3>
                <p className="text-sm text-muted-foreground">Check back later for new content</p>
              </CardContent>
            </Card>
          ) : (
            updates.map((update, idx) => (
              <Card key={idx} className="hover:bg-card cursor-pointer transition-colors" onClick={() => update.case_id && navigate(`/case/${update.case_id}`)}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="secondary" className="text-xs">{update.type || 'Update'}</Badge>
                        <span className="text-xs text-muted-foreground">{new Date(update.date).toLocaleDateString()}</span>
                      </div>
                      <h3 className="font-medium text-foreground">{update.title}</h3>
                      <p className="text-sm text-muted-foreground mt-1">{update.description}</p>
                    </div>
                    <ArrowRight size={16} className="text-muted-foreground shrink-0 mt-1" />
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </SidebarLayout>
  );
}
