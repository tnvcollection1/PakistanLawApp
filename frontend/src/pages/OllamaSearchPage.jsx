import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Loader2, Sparkles, Bot, Send, Scale, Clock, ChevronRight, ExternalLink, Zap, Brain, MessageSquare, AlertCircle, CheckCircle2, RefreshCw } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import SidebarLayout from '../components/SidebarLayout';
import SEOHead from '../components/SEOHead';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const OllamaSearchPage = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [chatMode, setChatMode] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [ollamaStatus, setOllamaStatus] = useState(null);
  const searchInputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => { checkOllamaStatus(); }, []);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [chatHistory]);

  const checkOllamaStatus = async () => {
    try { const r = await fetch(`${API_URL}/api/ollama/status`); const d = await r.json(); setOllamaStatus(d); }
    catch (err) { setOllamaStatus({ status: 'error' }); }
  };

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim() || loading) return;
    setLoading(true); setError(null); setResult(null);
    try {
      const r = await fetch(`${API_URL}/api/ollama/search`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: query.trim(), limit: 5 }) });
      if (!r.ok) throw new Error('Search failed');
      const d = await r.json(); setResult(d);
    } catch (err) { setError('Search failed. Please try again.'); console.error(err); }
    finally { setLoading(false); }
  };

  const handleChat = async (e) => {
    e?.preventDefault();
    if (!chatInput.trim() || chatLoading) return;
    const msg = chatInput.trim();
    setChatInput(''); setChatHistory(prev => [...prev, { role: 'user', content: msg }]);
    setChatLoading(true);
    try {
      const r = await fetch(`${API_URL}/api/ollama/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: msg }) });
      if (!r.ok) throw new Error('Chat failed');
      const d = await r.json();
      setChatHistory(prev => [...prev, { role: 'assistant', content: d.response }]);
    } catch (err) { setChatHistory(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]); }
    finally { setChatLoading(false); }
  };

  const suggestedQueries = ["What is bail in murder case?", "Punishment for theft under PPC", "Rights of accused in Pakistan", "Section 302 PPC explained", "Divorce law in Pakistan"];

  return (
    <SidebarLayout>
      <SEOHead title="AI Legal Search - PakistanLawApp" description="Free AI-powered legal research assistant for Pakistani law" />
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
        <div className="bg-white border-b border-slate-200 sticky top-0 z-10">
          <div className="max-w-6xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center"><Brain className="w-5 h-5 text-white" /></div>
                <div><h1 className="text-xl font-bold text-slate-800">AI Legal Assistant</h1><p className="text-xs text-slate-500">Powered by Ollama • Local AI</p></div>
              </div>
              <div className="flex items-center gap-2">
                {ollamaStatus?.status === 'running' ? (
                  <span className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium"><CheckCircle2 size={14} /> AI Online</span>
                ) : (
                  <span className="flex items-center gap-1.5 px-3 py-1.5 bg-red-50 text-red-700 rounded-full text-xs font-medium"><AlertCircle size={14} /> AI Offline</span>
                )}
                <div className="flex bg-slate-100 rounded-lg p-1">
                  <button onClick={() => setChatMode(false)} className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${!chatMode ? 'bg-white shadow text-slate-800' : 'text-slate-500 hover:text-slate-700'}`}><Search size={14} className="inline mr-1" /> Search</button>
                  <button onClick={() => setChatMode(true)} className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${chatMode ? 'bg-white shadow text-slate-800' : 'text-slate-500 hover:text-slate-700'}`}><MessageSquare size={14} className="inline mr-1" /> Chat</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="max-w-4xl mx-auto px-4 py-8">
          {!chatMode ? (
            <>
              <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 border border-slate-200 p-6 mb-6">
                <form onSubmit={handleSearch} className="flex gap-3">
                  <div className="flex-1 relative"><Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} /><Input ref={searchInputRef} value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ask any legal question in plain English..." className="pl-12 h-14 text-lg border-slate-200 rounded-xl focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500" /></div>
                  <Button type="submit" disabled={loading || !query.trim()} className="h-14 px-8 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 rounded-xl font-medium">{loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <><Sparkles size={18} className="mr-2" /> Search</>}</Button>
                </form>
                {!result && !loading && (
                  <div className="mt-4 flex flex-wrap gap-2">{suggestedQueries.map((sq, i) => (<button key={i} onClick={() => setQuery(sq)} className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 text-slate-600 text-sm rounded-lg transition-colors">{sq}</button>))}</div>
                )}
              </div>
              {loading && (
                <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8 text-center"><Loader2 className="w-12 h-12 animate-spin text-violet-500 mx-auto mb-4" /><h3 className="text-lg font-semibold text-slate-800 mb-2">AI is analyzing your question...</h3><p className="text-slate-500 text-sm">Searching through Pakistani case law database</p><p className="text-slate-400 text-xs mt-2">This may take 15-30 seconds</p></div>
              )}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 flex items-center gap-3"><AlertCircle size={20} /> {error} <Button variant="ghost" size="sm" onClick={handleSearch} className="ml-auto"><RefreshCw size={14} className="mr-1" /> Retry</Button></div>
              )}
              {result && (
                <div className="space-y-6">
                  <div className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-2xl border border-violet-200 p-6">
                    <div className="flex items-center gap-2 mb-4"><div className="w-8 h-8 rounded-lg bg-violet-500 flex items-center justify-center"><Bot size={18} className="text-white" /></div><div><h3 className="font-semibold text-slate-800">AI Answer</h3><p className="text-xs text-slate-500">Model: {result.model}</p></div></div>
                    <div className="prose prose-slate prose-sm max-w-none"><p className="text-slate-700 leading-relaxed whitespace-pre-wrap">{result.ai_answer || 'No answer generated.'}</p></div>
                  </div>
                  {result.cases && result.cases.length > 0 && (
                    <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-6">
                      <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2"><Scale size={18} className="text-amber-500" /> Related Cases ({result.cases.length})</h3>
                      <div className="space-y-4">
                        {result.cases.map((c, i) => (
                          <div key={i} onClick={() => navigate(`/case/${c.case_id}`)} className="p-4 bg-slate-50 hover:bg-slate-100 rounded-xl cursor-pointer transition-colors group">
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">{c.citation && <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-medium rounded">{c.citation}</span>}{c.year && <span className="text-xs text-slate-500">{c.year}</span>}</div>
                                <h4 className="font-medium text-slate-800 truncate">{c.parties || 'Untitled Case'}</h4>
                                <p className="text-sm text-slate-500 mt-1">{c.court}</p>
                                {c.headnotes && <p className="text-sm text-slate-600 mt-2 line-clamp-2">{c.headnotes}</p>}
                              </div>
                              <ChevronRight size={20} className="text-slate-400 group-hover:text-violet-500 transition-colors flex-shrink-0" />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="bg-white rounded-2xl shadow-lg border border-slate-200 overflow-hidden" style={{ height: 'calc(100vh - 200px)' }}>
              <div className="flex-1 overflow-y-auto p-6 space-y-4" style={{ height: 'calc(100% - 80px)' }}>
                {chatHistory.length === 0 && (
                  <div className="text-center py-12"><Bot size={48} className="mx-auto text-slate-300 mb-4" /><h3 className="text-lg font-medium text-slate-600">Start a conversation</h3><p className="text-slate-400 text-sm mt-1">Ask me anything about Pakistani law</p>
                    <div className="mt-6 flex flex-wrap justify-center gap-2">{['What is Section 302 PPC?', 'Explain bail process', 'Rights of accused'].map((q, i) => (<button key={i} onClick={() => setChatInput(q)} className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 text-sm rounded-lg transition-colors">{q}</button>))}</div>
                  </div>
                )}
                {chatHistory.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${msg.role === 'user' ? 'bg-violet-600 text-white rounded-br-md' : 'bg-slate-100 text-slate-800 rounded-bl-md'}`}>
                      {msg.role === 'assistant' && <div className="flex items-center gap-1.5 mb-1.5"><Bot size={14} className="text-violet-500" /><span className="text-xs font-medium text-violet-600">AI Assistant</span></div>}
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex justify-start"><div className="bg-slate-100 rounded-2xl rounded-bl-md px-4 py-3"><div className="flex items-center gap-2"><Loader2 size={16} className="animate-spin text-violet-500" /><span className="text-sm text-slate-500">Thinking...</span></div></div></div>
                )}
                <div ref={chatEndRef} />
              </div>
              <div className="border-t border-slate-200 p-4 bg-slate-50">
                <form onSubmit={handleChat} className="flex gap-3"><Input value={chatInput} onChange={(e) => setChatInput(e.target.value)} placeholder="Type your legal question..." className="flex-1 h-12 rounded-xl border-slate-200" disabled={chatLoading} /><Button type="submit" disabled={chatLoading || !chatInput.trim()} className="h-12 px-6 bg-violet-600 hover:bg-violet-700 rounded-xl"><Send size={18} /></Button></form>
              </div>
            </div>
          )}
          <div className="mt-8 text-center"><p className="text-xs text-slate-400">Powered by <span className="font-medium">Ollama phi3:mini</span> • Running locally on our servers • Local AI</p></div>
        </div>
      </div>
    </SidebarLayout>
  );
};

export default OllamaSearchPage;
