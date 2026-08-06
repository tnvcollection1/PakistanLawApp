import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { getAlerts, updateAlert } from '@/services/alertService';

const AlertsPage = () => {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    getAlerts().then(setAlerts);
  }, []);

  const toggleAlert = async (id) => {
    const alert = alerts.find(a => a.id === id);
    if (!alert) return;
    await updateAlert(id, { enabled: !alert.enabled });
    setAlerts(alerts.map(a => a.id === id ? { ...a, enabled: !a.enabled } : a));
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Alerts</h1>
      <div className="space-y-3">
        {alerts.map(alert => (
          <Card key={alert.id} className="p-4 flex justify-between items-center">
            <div>
              <h3 className="font-bold">{alert.name}</h3>
              <p className="text-sm text-muted-foreground">{alert.query}</p>
              <Badge variant={alert.enabled ? 'default' : 'outline'}>
                {alert.enabled ? 'Active' : 'Disabled'}
              </Badge>
            </div>
            <Switch checked={alert.enabled} onCheckedChange={() => toggleAlert(alert.id)} />
          </Card>
        ))}
      </div>
    </div>
  );
};

export default AlertsPage;
