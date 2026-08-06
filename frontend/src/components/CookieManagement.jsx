import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import { useToast } from '../components/ui/use-toast';
import { Cookie, Shield, Info, Trash2 } from 'lucide-react';

const CookieManagement = () => {
  const { toast } = useToast();
  const [cookies, setCookies] = useState({
    essential: true,
    analytics: false,
    marketing: false,
    preferences: false
  });
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    // Load cookie preferences from storage
    const saved = localStorage.getItem('cookie-preferences');
    if (saved) {
      try {
        setCookies(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to parse cookie preferences');
      }
    }
  }, []);

  const handleToggle = (type) => {
    if (type === 'essential') return; // Cannot disable essential cookies
    
    setCookies(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  const handleSave = () => {
    localStorage.setItem('cookie-preferences', JSON.stringify(cookies));
    
    // Apply cookie settings
    if (cookies.analytics) {
      enableAnalytics();
    } else {
      disableAnalytics();
    }
    
    if (cookies.marketing) {
      enableMarketing();
    } else {
      disableMarketing();
    }
    
    toast({
      title: "Preferences Saved",
      description: "Your cookie preferences have been updated."
    });
  };

  const handleAcceptAll = () => {
    const allEnabled = {
      essential: true,
      analytics: true,
      marketing: true,
      preferences: true
    };
    
    setCookies(allEnabled);
    localStorage.setItem('cookie-preferences', JSON.stringify(allEnabled));
    
    enableAnalytics();
    enableMarketing();
    
    toast({
      title: "All Cookies Enabled",
      description: "You have accepted all cookies."
    });
  };

  const handleRejectAll = () => {
    const minimal = {
      essential: true,
      analytics: false,
      marketing: false,
      preferences: false
    };
    
    setCookies(minimal);
    localStorage.setItem('cookie-preferences', JSON.stringify(minimal));
    
    disableAnalytics();
    disableMarketing();
    
    toast({
      title: "Non-Essential Cookies Disabled",
      description: "Only essential cookies are now active."
    });
  };

  const handleClearAll = () => {
    // Clear all cookies
    document.cookie.split(';').forEach(cookie => {
      const [name] = cookie.split('=');
      document.cookie = `${name.trim()}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    });
    
    localStorage.removeItem('cookie-preferences');
    
    setCookies({
      essential: true,
      analytics: false,
      marketing: false,
      preferences: false
    });
    
    toast({
      title: "All Cookies Cleared",
      description: "All cookies have been removed."
    });
  };

  const enableAnalytics = () => {
    console.log('Analytics enabled');
    // Implement analytics initialization
  };

  const disableAnalytics = () => {
    console.log('Analytics disabled');
    // Implement analytics cleanup
  };

  const enableMarketing = () => {
    console.log('Marketing enabled');
    // Implement marketing initialization
  };

  const disableMarketing = () => {
    console.log('Marketing disabled');
    // Implement marketing cleanup
  };

  const cookieTypes = [
    {
      id: 'essential',
      name: 'Essential Cookies',
      description: 'Required for the website to function properly. Cannot be disabled.',
      icon: Shield,
      required: true
    },
    {
      id: 'analytics',
      name: 'Analytics Cookies',
      description: 'Help us understand how visitors interact with our website.',
      icon: Info
    },
    {
      id: 'marketing',
      name: 'Marketing Cookies',
      description: 'Used to deliver relevant advertisements and track their performance.',
      icon: Info
    },
    {
      id: 'preferences',
      name: 'Preference Cookies',
      description: 'Remember your settings and preferences for a better experience.',
      icon: Info
    }
  ];

  return (
    <Card className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <Cookie className="w-6 h-6 text-blue-600" />
        <div>
          <h2 className="text-xl font-semibold">Cookie Preferences</h2>
          <p className="text-sm text-slate-600">
            Manage how we use cookies on our website
          </p>
        </div>
      </div>

      <div className="space-y-4 mb-6">
        {cookieTypes.map(type => (
          <div
            key={type.id}
            className="flex items-center justify-between p-4 bg-slate-50 rounded-lg"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <type.icon className="w-4 h-4 text-slate-600" />
                <Label htmlFor={type.id} className="font-medium cursor-pointer">
                  {type.name}
                  {type.required && (
                    <span className="ml-2 text-xs text-slate-500">(Required)</span>
                  )}
                </Label>
              </div>
              <p className="text-sm text-slate-600 mt-1 ml-6">
                {type.description}
              </p>
            </div>
            <Switch
              id={type.id}
              checked={cookies[type.id]}
              onCheckedChange={() => handleToggle(type.id)}
              disabled={type.required}
            />
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-3">
        <Button onClick={handleSave}>
          Save Preferences
        </Button>
        <Button variant="outline" onClick={handleAcceptAll}>
          Accept All
        </Button>
        <Button variant="outline" onClick={handleRejectAll}>
          Reject All
        </Button>
        <Button variant="destructive" onClick={handleClearAll}>
          <Trash2 className="w-4 h-4 mr-2" />
          Clear All
        </Button>
      </div>

      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-start gap-2">
          <Info className="w-4 h-4 text-blue-600 mt-0.5" />
          <p className="text-sm text-blue-800">
            Essential cookies are necessary for the website to function and cannot be disabled. 
            Other cookies help us improve your experience and are only used with your consent.
          </p>
        </div>
      </div>
    </Card>
  );
};

export default CookieManagement;
