import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import SidebarLayout from '../components/SidebarLayout';
import { Send, Loader2, Bot, User, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function ChatbotPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your Pakistani legal research assistant. Ask me about case law, statutes, or legal concepts.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch(`${API}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg,
          username: user?.username || 'anonymous'
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Network error. Please check your connection.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background flex flex-col">
        <div className="bg-white dark:bg-background border-b shadow-sm px-4 sm:px-6 py-4">
          <div className="max-w-3xl mx-auto flex items-center gap-2">
            <Bot size={20} className="text-primary" />
            <h1 className="text-lg font-semibold text-foreground">Legal AI Assistant</h1>
            <Sparkles size={16} className="text-yellow-500" />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4">
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                    <Bot size={16} className="text-primary" />
                  </div>
                )}
                <Card className={`max-w-[80%] ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-card'}`}>
                  <CardContent className="p-3 text-sm">
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  </CardContent>
                </Card>
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
                    <User size={16} className="text-slate-600" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <Bot size={16} className="text-primary" />
                </div>
                <Card className="bg-card">
                  <CardContent className="p-3">
                    <Loader2 size={16} className="animate-spin text-primary" />
                  </CardContent>
                </Card>
              </div>
            )}
            <div ref={scrollRef} />
          </div>
        </div>

        <div className="bg-white dark:bg-background border-t px-4 sm:px-6 py-4">
          <form onSubmit={sendMessage} className="max-w-3xl mx-auto flex gap-2">
            <Input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask a legal question..."
              className="flex-1"
              disabled={loading}
            />
            <Button type="submit" disabled={loading || !input.trim()} className="bg-primary hover:bg-primary/90">
              <Send size={16} />
            </Button>
          </form>
        </div>
      </div>
    </SidebarLayout>
  );
}
