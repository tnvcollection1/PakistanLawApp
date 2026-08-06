import React, { useState, useRef, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { sendChatMessage } from '@/services/chatService';

const ChatbotPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    const response = await sendChatMessage(input);
    setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto flex flex-col h-[80vh]">
      <h1 className="text-3xl font-bold mb-4">Legal Chatbot</h1>
      <div className="flex-1 overflow-y-auto border rounded p-4 mb-4 space-y-3">
        {messages.map((msg, i) => (
          <Card key={i} className={`p-3 ${msg.role === 'user' ? 'ml-auto bg-primary text-white' : 'mr-auto'}`}>
            <p>{msg.content}</p>
          </Card>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="flex gap-2">
        <Input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask a legal question..." onKeyPress={(e) => e.key === 'Enter' && handleSend()} />
        <Button onClick={handleSend} disabled={loading}>{loading ? '...' : 'Send'}</Button>
      </div>
    </div>
  );
};

export default ChatbotPage;
