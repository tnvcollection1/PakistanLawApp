import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { getAIHeadnotes } from '@/services/aiService';

const AIHeadnotesPage = () => {
  const [text, setText] = useState('');
  const [headnotes, setHeadnotes] = useState([]);
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    if (!text.trim()) return;
    setGenerating(true);
    const result = await getAIHeadnotes(text);
    setHeadnotes(result);
    setGenerating(false);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">AI Headnotes Generator</h1>
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste case text to generate headnotes..."
        className="mb-4"
        rows={10}
      />
      <Button onClick={handleGenerate} disabled={generating} className="mb-4">
        {generating ? 'Generating...' : 'Generate Headnotes'}
      </Button>
      <div className="space-y-3">
        {headnotes.map((hn, i) => (
          <Card key={i} className="p-4">
            <h3 className="font-bold">Headnote {i + 1}</h3>
            <p>{hn.text}</p>
            <p className="text-sm text-muted-foreground mt-1">Topics: {hn.topics?.join(', ')}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default AIHeadnotesPage;
