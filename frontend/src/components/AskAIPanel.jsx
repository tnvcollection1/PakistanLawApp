import React, { useState } from 'react';

export default function AskAIPanel() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const askAI = async () => {
    setAnswer('AI is thinking...');
    // Placeholder for AI integration
    setTimeout(() => setAnswer('This is a placeholder response. AI integration will be added soon.'), 1000);
  };

  return (
    <div className="bg-white rounded-lg border p-4">
      <h3 className="font-semibold mb-2">Ask AI</h3>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question about this case..."
        className="w-full border rounded px-3 py-2 mb-2"
      />
      <button onClick={askAI} className="bg-blue-600 text-white px-4 py-2 rounded">Ask</button>
      {answer && <p className="mt-2 text-sm text-gray-600">{answer}</p>}
    </div>
  );
}
