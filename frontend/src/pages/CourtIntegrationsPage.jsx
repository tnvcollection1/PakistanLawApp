import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import SidebarLayout from '../components/SidebarLayout';
import { Link2, CheckCircle, XCircle, RefreshCw, ExternalLink } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL || '';

const COURT_INTEGRATIONS = [
  {
    name: 'Pakistan Law Site',
    url: 'https://www.pakistanlawsite.com',
    status: 'active',
    cases: '194K+',
    description: 'Official PLS case database with 194,167 judgments',
  },
  {
    name: 'EastLaw',
    url: 'https://www.eastlaw.pk',
    status: 'active',
    cases: '231K+',
    description: 'Cross-referenced case law database',
  },
  {
    name: 'Sindh High Court',
    url: 'https://caselaw.shc.gov.pk',
    status: 'pending',
    cases: 'In progress',
    description: 'Sindh High Court reported judgments portal',
  },
  {
    name: 'Lahore High Court',
    url: 'https://caselaw.lhc.gov.pk',
    status: 'planned',
    cases: 'Coming soon',
    description: 'Lahore High Court digital case repository',
  },
  {
    name: 'Supreme Court',
    url: 'https://www.supremecourt.gov.pk',
    status: 'planned',
    cases: 'Coming soon',
    description: 'Supreme Court of Pakistan case database',
  },
];

export default function CourtIntegrationsPage() {
  const [status, setStatus] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API}/api/integrations/status`);
      if (res.ok) setStatus(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircle size={16} className="text-emerald-500" />;
      case 'pending': return <RefreshCw size={16} className="text-amber-500" />;
      case 'planned': return <XCircle size={16} className="text-slate-400" />;
      default: return <XCircle size={16} className="text-red-500" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active': return <Badge variant="default" className="bg-emerald-500 text-white">Active</Badge>;
      case 'pending': return <Badge variant="outline" className="text-amber-600 border-amber-600">In Progress</Badge>;
      case 'planned': return <Badge variant="outline" className="text-slate-400 border-slate-400">Planned</Badge>;
      default: return <Badge variant="outline" className="text-red-500 border-red-500">Error</Badge>;
    }
  };

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background">
        <div className="bg-white dark:bg-background border-b shadow-sm px-4 sm:px-6 py-4 sm:py-5">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-lg sm:text-xl font-semibold text-slate-800 dark:text-foreground flex items-center gap-2">
              <Link2 size={20} className="text-slate-800 dark:text-foreground" /> Court Integrations
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-1">Connected court databases and data sources</p>
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4 sm:py-8 space-y-4">
          {loading ? (
            <div className="flex justify-center py-12"><RefreshCw className="w-8 h-8 animate-spin text-primary" /></div>
          ) : (
            COURT_INTEGRATIONS.map((integration, idx) => (
              <Card key={idx}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-primary/10 mt-0.5">
                        <Link2 size={16} className="text-primary" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium text-foreground">{integration.name}</h3>
                          {getStatusBadge(integration.status)}
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">{integration.description}</p>
                        <div className="flex items-center gap-4 mt-2">
                          <span className="text-xs text-muted-foreground">Cases: {integration.cases}</span>
                          <a href={integration.url} target="_blank" rel="noopener noreferrer" className="text-xs text-primary hover:underline flex items-center gap-1">
                            <ExternalLink size={10} /> Visit site
                          </a>
                        </div>
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      {getStatusIcon(integration.status)}
                    </div>
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
