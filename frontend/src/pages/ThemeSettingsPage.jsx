import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { useTheme } from '@/context/ThemeContext';

const ThemeSettingsPage = () => {
  const { theme, toggleTheme } = useTheme();
  const [settings, setSettings] = useState({
    compactMode: false,
    showPreviews: true,
    highContrast: false,
  });

  const toggleSetting = (key) => {
    setSettings(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Theme Settings</h1>
      <div className="space-y-4">
        <Card className="p-4 flex justify-between items-center">
          <div>
            <h3 className="font-bold">Dark Mode</h3>
            <p className="text-sm text-muted-foreground">Toggle dark/light theme</p>
          </div>
          <Switch checked={theme === 'dark'} onCheckedChange={toggleTheme} />
        </Card>
        <Card className="p-4 flex justify-between items-center">
          <div>
            <h3 className="font-bold">Compact Mode</h3>
            <p className="text-sm text-muted-foreground">Reduce spacing for dense view</p>
          </div>
          <Switch checked={settings.compactMode} onCheckedChange={() => toggleSetting('compactMode')} />
        </Card>
        <Card className="p-4 flex justify-between items-center">
          <div>
            <h3 className="font-bold">Show Previews</h3>
            <p className="text-sm text-muted-foreground">Display case previews in search results</p>
          </div>
          <Switch checked={settings.showPreviews} onCheckedChange={() => toggleSetting('showPreviews')} />
        </Card>
        <Card className="p-4 flex justify-between items-center">
          <div>
            <h3 className="font-bold">High Contrast</h3>
            <p className="text-sm text-muted-foreground">Increase contrast for accessibility</p>
          </div>
          <Switch checked={settings.highContrast} onCheckedChange={() => toggleSetting('highContrast')} />
        </Card>
      </div>
    </div>
  );
};

export default ThemeSettingsPage;
