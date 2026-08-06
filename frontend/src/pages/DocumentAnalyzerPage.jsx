import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { analyzeDocument } from '@/services/aiService';

const DocumentAnalyzerPage = () => {
  const [text, setText] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setAnalyzing(true);
    const result = await analyzeDocument(text);
    setAnalysis(result);
    setAnalyzing(false);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Document Analyzer</h1>
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste legal document text here..."
        className="mb-4"
        rows={10}
      />
      <Button onClick={handleAnalyze} disabled={analyzing} className="mb-4">
        {analyzing ? 'Analyzing...' : 'Analyze'}
      </Button>
      {analysis && (
        <div className="space-y-4">
          <Card className="p-4">
            <h3 className="font-bold">Summary</h3>
            <p>{analysis.summary}</p>
          </Card>
          <Card className="p-4">
            <h3 className="font-bold">Key Issues</h3>
            <ul className="list-disc pl-5">
              {analysis.issues?.map((issue, i) => <li key={i}>{issue}</li>)}
            </ul>
          </Card>
          <Card className="p-4">
            <h3 className="font-bold">Citations</h3>
            <ul className="list-disc pl-5">
              {analysis.citations?.map((cite, i) => <li key={i}>{cite}</li>)}
            </ul>
          </Card>
        </div>
      )}
    </div>
  );
};

export default DocumentAnalyzerPage;
