import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { useTheme } from '@/context/ThemeContext';

const ThemePreview = () => {
  const { theme, toggleTheme } = useTheme();
  const [compact, setCompact] = useState(false);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Theme Preview</h1>
      <div className="flex gap-4 mb-6">
        <Card className="p-4 flex items-center gap-2">
          <span>Dark Mode</span>
          <Switch checked={theme === 'dark'} onCheckedChange={toggleTheme} />
        </Card>
        <Card className="p-4 flex items-center gap-2">
          <span>Compact</span>
          <Switch checked={compact} onCheckedChange={() => setCompact(!compact)} />
        </Card>
      </div>
      <div className={`space-y-4 ${compact ? 'space-y-1' : 'space-y-4'}`}>
        <Card className="p-4">
          <h3 className="font-bold">Preview Card</h3>
          <p className="text-sm text-muted-foreground">This is how cards look in the current theme.</p>
        </Card>
        <Card className="p-4">
          <h3 className="font-bold">Another Preview</h3>
          <p className="text-sm text-muted-foreground">Notice spacing changes with compact mode.</p>
        </Card>
      </div>
    </div>
  );
};

export default ThemePreview;
