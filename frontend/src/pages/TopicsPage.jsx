import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import SidebarLayout from '../components/SidebarLayout';
import { Hash, ArrowRight, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function TopicsPage() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchTopics();
  }, []);

  const fetchTopics = async () => {
    try {
      const res = await fetch(`${API}/api/topics`);
      if (res.ok) {
        const data = await res.json();
        setTopics(data.topics || []);
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
              <Hash size={20} className="text-primary" /> Legal Topics
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-1">Browse cases by topic and subject matter</p>
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4 sm:py-8">
          {loading ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {topics.map((topic, idx) => (
                <Card key={idx} className="hover:bg-card cursor-pointer transition-colors" onClick={() => navigate(`/topic/${encodeURIComponent(topic.name)}`)}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                          <Hash size={16} className="text-primary" />
                        </div>
                        <div>
                          <h3 className="font-medium text-foreground">{topic.name}</h3>
                          <p className="text-sm text-muted-foreground">{topic.case_count} cases</p>
                        </div>
                      </div>
                      <ArrowRight size={16} className="text-muted-foreground" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </SidebarLayout>
  );
}
