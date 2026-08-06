import React, { useState } from 'react';

export default function AskAIPanel() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    setLoading(true);
    // Simulate AI call
    setTimeout(() => {
      setAnswer('This is a simulated AI response to your legal question.');
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="p-4 border rounded-lg bg-card">
      <h3 className="font-semibold mb-2">Ask AI</h3>
      <textarea
        className="w-full p-2 border rounded mb-2"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a legal question..."
      />
      <button
        onClick={handleAsk}
        disabled={loading}
        className="px-4 py-2 bg-primary text-primary-foreground rounded"
      >
        {loading ? 'Thinking...' : 'Ask'}
      </button>
      {answer && (
        <div className="mt-4 p-3 bg-muted rounded">
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}
