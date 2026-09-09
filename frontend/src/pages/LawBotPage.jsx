import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  MessageCircle, X, Send, Loader, Bot, User, Search,
  Zap, Globe, BookOpen, Scale, ChevronRight, Sparkles,
  History, Bookmark, Copy, Check, Mic, Volume2,
  ArrowRight, Gavel, FileText, Briefcase, Home,
  Shield, TrendingUp, BarChart3, ExternalLink,
} from "lucide-react";

const API_BASE = process.env.REACT_APP_API_URL || "/api";

const SUGGESTED_QUESTIONS = [
  "How can a person obtain bail in a criminal case in Pakistan?",
  "Explain Section 302 PPC - Punishment for qatl-e-amd",
  "What is the procedure for filing a constitutional petition under Article 199?",
  "What are the grounds for divorce under Muslim Family Laws Ordinance?",
  "How to challenge a conviction in the Supreme Court of Pakistan?",
  "Explain the doctrine of stare decisis in Pakistani courts",
  "What are the requirements for a valid sale deed?",
  "How does NAB investigate corruption cases?",
  "What is the difference between revisional and appellate jurisdiction?",
  "Explain the concept of Qisas and Diyat under Pakistani law",
];

const QUICK_ACTIONS = [
  { id: "explain_section", label: "Explain Section", icon: FileText, color: "bg-blue-100 text-blue-700" },
  { id: "find_precedent", label: "Find Precedent", icon: Gavel, color: "bg-amber-100 text-amber-700" },
  { id: "procedure_guide", label: "Procedure Guide", icon: BookOpen, color: "bg-green-100 text-green-700" },
  { id: "draft_petition", label: "Draft Petition", icon: Briefcase, color: "bg-purple-100 text-purple-700" },
];

export default function LawBotPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "**Assalam-o-Alaikum!** I am **PakistanLawBot**, your AI legal research assistant trained on **369,810+ Pakistani case laws**, statutes, and legal terms.\n\nI can help you with:\n- Case law research and citation\n- Statute interpretation (PPC, Cr.P.C, Constitution, etc.)\n- Legal procedure guidance\n- Drafting petitions and applications\n- Finding relevant precedents\n\n**How may I assist you today?**",
      sources: [],
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("normal");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [stats, setStats] = useState({ cases: 369810, statutes: 32079, terms: 38179 });
  const [copiedIndex, setCopiedIndex] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetch(`${API_BASE}/lawbot/health`)
      .then((r) => r.json())
      .then((data) => {
        if (data.cases_loaded) {
          setStats((s) => ({ ...s, cases: data.cases_loaded }));
        }
      })
      .catch(() => {});
  }, []);

  const sendMessage = async (text = input) => {
    if (!text.trim() || loading) return;

    const userMessage = {
      role: "user",
      content: text.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const history = messages
        .filter((m) => m.role !== "system")
        .slice(-10)
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch(`${API_BASE}/lawbot/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text.trim(),
          history,
          mode,
          session_id: `session_${Date.now()}`,
        }),
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response || "I apologize, but I could not process your request.",
          sources: data.sources || [],
          model: data.model,
          searched_cases: data.searched_cases,
          response_time: data.response_time_ms,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I apologize, but I'm having trouble connecting to the legal database. Please try again in a moment.",
          sources: [],
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const startNewChat = () => {
    setMessages([
      {
        role: "assistant",
        content: "**Assalam-o-Alaikum!** I am **PakistanLawBot**, your AI legal research assistant trained on **369,810+ Pakistani case laws**, statutes, and legal terms.\n\nI can help you with:\n- Case law research and citation\n- Statute interpretation (PPC, Cr.P.C, Constitution, etc.)\n- Legal procedure guidance\n- Drafting petitions and applications\n- Finding relevant precedents\n\n**How may I assist you today?**",
        sources: [],
        timestamp: new Date().toISOString(),
      },
    ]);
    setInput("");
    inputRef.current?.focus();
  };

  const formatContent = (content) => {
    if (!content) return "";
    let formatted = content
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/^\>\s*(.+)$/gm, "<blockquote class='border-l-4 border-[#c9a227] pl-3 my-2 text-gray-600 italic'>$1</blockquote>")
      .replace(/^(\d+\.\s*.+)$/gm, "<div class='my-1'>$1</div>")
      .replace(/^(\-\s*.+)$/gm, "<div class='my-1 ml-2'>$1</div>");
    return formatted;
  };

  return (
    <div className="flex h-screen bg-[#f8f9fa]">
      <aside
        className={`${
          sidebarOpen ? "w-72" : "w-0"
        } bg-white border-r border-gray-200 flex flex-col transition-all duration-300 overflow-hidden`}
      >
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#1a365d] rounded-lg flex items-center justify-center">
              <Scale className="w-5 h-5 text-[#c9a227]" />
            </div>
            <div>
              <h1 className="font-bold text-[#1a365d] text-sm">PakistanLawBot</h1>
              <p className="text-xs text-gray-400">AI Legal Research</p>
            </div>
          </div>
        </div>

        <div className="p-3">
          <button
            onClick={startNewChat}
            className="w-full flex items-center justify-center gap-2 bg-[#1a365d] text-white py-2.5 px-4 rounded-lg hover:bg-[#234e8e] transition text-sm font-medium"
          >
            <Sparkles size={16} />
            Start A New Chat
          </button>
        </div>

        <div className="px-3 pb-2">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-2">Quick Actions</p>
          {QUICK_ACTIONS.map((action) => {
            const Icon = action.icon;
            return (
              <button
                key={action.id}
                onClick={() => sendMessage(`${action.label}: `)}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-left text-sm text-gray-700 transition mb-1"
              >
                <div className={`w-7 h-7 rounded-md ${action.color} flex items-center justify-center`}>
                  <Icon size={14} />
                </div>
                {action.label}
              </button>
            );
          })}
        </div>

        <div className="mt-auto p-4 border-t border-gray-100">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 size={14} className="text-[#1a365d]" />
              <span className="text-xs font-semibold text-[#1a365d]">Database Stats</span>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Cases</span>
                <span className="font-medium text-[#1a365d]">{stats.cases.toLocaleString()}+</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Statutes</span>
                <span className="font-medium text-[#1a365d]">{stats.statutes.toLocaleString()}+</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Legal Terms</span>
                <span className="font-medium text-[#1a365d]">{stats.terms.toLocaleString()}+</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 flex flex-col min-w-0">
        <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
            >
              <MessageCircle size={18} className="text-gray-600" />
            </button>
            <div>
              <h2 className="font-semibold text-[#1a365d] text-sm">PakistanLawBot</h2>
              <p className="text-xs text-gray-400">Trained on Pakistani law - {stats.cases.toLocaleString()}+ cases</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setMode("normal")}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
                  mode === "normal" ? "bg-white text-[#1a365d] shadow-sm" : "text-gray-500 hover:text-gray-700"
                }`}
              >
                Normal
              </button>
              <button
                onClick={() => setMode("web_search")}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition flex items-center gap-1 ${
                  mode === "web_search" ? "bg-white text-[#1a365d] shadow-sm" : "text-gray-500 hover:text-gray-700"
                }`}
              >
                <Globe size={12} />
                Web Search
              </button>
              <button
                onClick={() => setMode("turbo")}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition flex items-center gap-1 ${
                  mode === "turbo" ? "bg-white text-[#1a365d] shadow-sm" : "text-gray-500 hover:text-gray-700"
                }`}
              >
                <Zap size={12} />
                Turbo
              </button>
            </div>

            <button
              onClick={() => navigate("/")}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
              title="Back to Home"
            >
              <Home size={18} className="text-gray-600" />
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message, i) => (
              <div key={i} className={`flex gap-4 ${message.role === "user" ? "flex-row-reverse" : ""}`}>
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.role === "user"
                      ? "bg-[#1a365d]"
                      : "bg-gradient-to-br from-[#c9a227] to-[#d4af37]"
                  }`}
                >
                  {message.role === "user" ? (
                    <User size={16} className="text-white" />
                  ) : (
                    <Bot size={16} className="text-white" />
                  )}
                </div>

                <div className={`max-w-[85%] ${message.role === "user" ? "items-end" : "items-start"}`}>
                  <div
                    className={`rounded-2xl px-5 py-3.5 ${
                      message.role === "user"
                        ? "bg-[#1a365d] text-white"
                        : "bg-white border border-gray-200 text-gray-800 shadow-sm"
                    }`}
                  >
                    <div
                      className="text-sm leading-relaxed whitespace-pre-wrap"
                      dangerouslySetInnerHTML={{
                        __html: formatContent(message.content),
                      }}
                    />
                  </div>

                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 space-y-1.5">
                      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Sources</p>
                      {message.sources.map((source, si) => (
                        <div
                          key={si}
                          className="bg-gray-50 border border-gray-100 rounded-lg px-3 py-2 flex items-center justify-between hover:bg-gray-100 transition cursor-pointer"
                          onClick={() => source.id && navigate(`/cases/${source.id}`)}
                        >
                          <div className="flex items-center gap-2 min-w-0">
                            {source.type === "case" && <Gavel size={12} className="text-[#c9a227] flex-shrink-0" />}
                            {source.type === "statute" && <BookOpen size={12} className="text-blue-500 flex-shrink-0" />}
                            {source.type === "term" && <FileText size={12} className="text-green-500 flex-shrink-0" />}
                            <span className="text-xs text-gray-700 truncate">
                              {source.citation || source.name || source.term}
                            </span>
                          </div>
                          {source.id && (
                            <ExternalLink size={12} className="text-gray-400 flex-shrink-0 ml-2" />
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="flex items-center gap-3 mt-1.5 px-1">
                    {message.model && (
                      <span className="text-[10px] text-gray-400">
                        {message.model}
                      </span>
                    )}
                    {message.searched_cases > 0 && (
                      <span className="text-[10px] text-gray-400 flex items-center gap-1">
                        <Search size={10} />
                        {message.searched_cases} cases searched
                      </span>
                    )}
                    {message.response_time > 0 && (
                      <span className="text-[10px] text-gray-400">
                        {message.response_time}ms
                      </span>
                    )}
                    <button
                      onClick={() => copyToClipboard(message.content, i)}
                      className="text-gray-400 hover:text-[#1a365d] transition"
                      title="Copy"
                    >
                      {copiedIndex === i ? <Check size={12} /> : <Copy size={12} />}
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex gap-4">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#c9a227] to-[#d4af37] flex items-center justify-center flex-shrink-0">
                  <Bot size={16} className="text-white" />
                </div>
                <div className="bg-white border border-gray-200 rounded-2xl px-5 py-3.5 shadow-sm">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Loader size={14} className="animate-spin text-[#1a365d]" />
                    <span>Searching {stats.cases.toLocaleString()}+ cases...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {messages.length <= 1 && (
          <div className="px-4 pb-4">
            <div className="max-w-4xl mx-auto">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Suggested Questions</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {SUGGESTED_QUESTIONS.slice(0, 6).map((q, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(q)}
                    className="text-left text-sm text-gray-600 bg-white border border-gray-200 rounded-lg px-4 py-3 hover:border-[#1a365d] hover:text-[#1a365d] transition"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="bg-white border-t border-gray-200 px-4 py-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end gap-3 bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus-within:border-[#1a365d] focus-within:ring-2 focus-within:ring-[#1a365d]/10 transition">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask any legal question... (e.g., How to file bail under Section 497 Cr.P.C?)"
                className="flex-1 bg-transparent resize-none outline-none text-sm text-gray-800 placeholder-gray-400 max-h-32"
                rows={1}
                style={{ minHeight: "24px" }}
              />
              <div className="flex items-center gap-2">
                {mode === "web_search" && (
                  <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">
                    Web Search
                  </span>
                )}
                {mode === "turbo" && (
                  <span className="text-[10px] bg-amber-100 text-amber-700 px-2 py-1 rounded-full font-medium">
                    Turbo
                  </span>
                )}
                <button
                  onClick={() => sendMessage()}
                  disabled={loading || !input.trim()}
                  className="bg-[#1a365d] text-white p-2.5 rounded-lg hover:bg-[#234e8e] disabled:opacity-40 disabled:cursor-not-allowed transition"
                >
                  {loading ? <Loader size={16} className="animate-spin" /> : <Send size={16} />}
                </button>
              </div>
            </div>
            <p className="text-[10px] text-gray-400 text-center mt-2">
              PakistanLawBot can make mistakes. Please verify critical information with a practicing advocate.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
