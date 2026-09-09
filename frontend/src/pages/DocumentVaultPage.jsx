import React, { useState, useEffect, useRef } from 'react';
import { Upload, FileText, MessageSquare, Trash2, Search, X, Send, Loader2, File } from 'lucide-react';
import api from '../api/api';

const DOC_TYPES = [
  { value: 'contract', label: 'Contract' },
  { value: 'judgment', label: 'Judgment' },
  { value: 'petition', label: 'Petition' },
  { value: 'notice', label: 'Legal Notice' },
  { value: 'fir', label: 'FIR' },
  { value: 'general', label: 'General' },
];

export default function DocumentVaultPage() {
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState({ total_documents: 0, by_type: {} });
  const [uploading, setUploading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const [uploadForm, setUploadForm] = useState({ title: '', description: '', doc_type: 'general' });
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
    fetchStats();
  }, [searchQuery]);

  const fetchDocuments = async () => {
    try {
      const res = await api.get('/vault/documents', {
        params: { keyword: searchQuery || undefined, limit: 100 }
      });
      setDocuments(res.data.data || []);
    } catch (e) {}
  };

  const fetchStats = async () => {
    try {
      const res = await api.get('/vault/stats');
      setStats(res.data);
    } catch (e) {}
  };

  const handleFileUpload = async () => {
    const file = fileInputRef.current?.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', uploadForm.title || file.name);
      formData.append('description', uploadForm.description);
      formData.append('doc_type', uploadForm.doc_type);
      await api.post('/vault/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setShowUpload(false);
      setUploadForm({ title: '', description: '', doc_type: 'general' });
      fileInputRef.current.value = '';
      fetchDocuments();
      fetchStats();
    } catch (e) {
      alert('Upload failed: ' + (e.response?.data?.detail || e.message));
    }
    setUploading(false);
  };

  const deleteDocument = async (id) => {
    if (!confirm('Delete this document?')) return;
    try {
      await api.delete(`/vault/documents/${id}`);
      if (selectedDoc?.id === id) setSelectedDoc(null);
      fetchDocuments();
      fetchStats();
    } catch (e) {}
  };

  const openDocumentChat = async (doc) => {
    setSelectedDoc(doc);
    try {
      const res = await api.get(`/vault/chat-history/${doc.id}`);
      setChatMessages(res.data.data || []);
    } catch (e) {
      setChatMessages([]);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !selectedDoc) return;
    const msg = chatInput.trim();
    setChatInput('');
    setChatLoading(true);
    setChatMessages(prev => [...prev, { message: msg, response: null, isUser: true }]);
    try {
      const res = await api.post('/vault/chat', {
        document_id: selectedDoc.id,
        message: msg,
      });
      setChatMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = { ...updated[updated.length - 1], response: res.data.response, isUser: false };
        return updated;
      });
    } catch (e) {
      setChatMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = { ...updated[updated.length - 1], response: 'Error: Could not get AI response.', isUser: false };
        return updated;
      });
    }
    setChatLoading(false);
  };

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2" style={{ color: 'var(--text-h)' }}>
          <FileText className="w-6 h-6 text-emerald-600" />
          Document Vault
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text)' }}>
          Upload legal documents and chat with them using AI
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="bg-white rounded-xl p-3 border shadow-sm">
          <div className="text-xs text-gray-500">Total Documents</div>
          <div className="text-xl font-bold">{stats.total_documents}</div>
        </div>
        {Object.entries(stats.by_type || {}).map(([type, count]) => (
          <div key={type} className="bg-white rounded-xl p-3 border shadow-sm">
            <div className="text-xs text-gray-500 capitalize">{type}</div>
            <div className="text-xl font-bold">{count}</div>
          </div>
        ))}
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          />
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 flex items-center gap-2"
        >
          <Upload className="w-4 h-4" /> Upload Document
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed rounded-xl">
          <FileText className="w-12 h-12 mx-auto mb-2 text-gray-300" />
          <p className="text-gray-500 text-sm">No documents yet. Upload your first legal document.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documents.map(doc => (
            <div
              key={doc.id}
              className="bg-white rounded-xl border p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => openDocumentChat(doc)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-sm line-clamp-1">{doc.title}</h3>
                    <p className="text-xs text-gray-500 capitalize">{doc.doc_type} • {(doc.size_bytes / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); deleteDocument(doc.id); }}
                  className="p-1 hover:bg-red-100 rounded"
                >
                  <Trash2 className="w-3.5 h-3.5 text-red-500" />
                </button>
              </div>
              {doc.description && (
                <p className="text-xs text-gray-500 mt-2 line-clamp-2">{doc.description}</p>
              )}
              <div className="flex gap-2 mt-3">
                <span className="text-xs px-2 py-0.5 bg-gray-100 rounded text-gray-600">
                  {new Date(doc.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showUpload && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold mb-4">Upload Document</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium mb-1">File (PDF, DOC, DOCX, TXT)</label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.doc,.docx,.txt"
                  className="w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-emerald-50 file:text-emerald-700"
                />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">Title</label>
                <input type="text" value={uploadForm.title} onChange={e => setUploadForm({ ...uploadForm, title: e.target.value })} className="w-full px-3 py-2 rounded-lg border text-sm" placeholder="Document title" />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">Type</label>
                <select value={uploadForm.doc_type} onChange={e => setUploadForm({ ...uploadForm, doc_type: e.target.value })} className="w-full px-3 py-2 rounded-lg border text-sm">
                  {DOC_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">Description</label>
                <textarea value={uploadForm.description} onChange={e => setUploadForm({ ...uploadForm, description: e.target.value })} rows={2} className="w-full px-3 py-2 rounded-lg border text-sm" placeholder="Optional description" />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={handleFileUpload} disabled={uploading} className="flex-1 py-2.5 bg-emerald-600 text-white rounded-lg font-medium text-sm hover:bg-emerald-700 disabled:opacity-50 flex items-center justify-center gap-2">
                {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                {uploading ? 'Uploading...' : 'Upload'}
              </button>
              <button onClick={() => setShowUpload(false)} className="flex-1 py-2.5 border rounded-lg font-medium text-sm hover:bg-gray-50">Cancel</button>
            </div>
          </div>
        </div>
      )}

      {selectedDoc && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-2xl h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-emerald-600" />
                <div>
                  <h3 className="font-medium text-sm">{selectedDoc.title}</h3>
                  <p className="text-xs text-gray-500">Ask questions about this document</p>
                </div>
              </div>
              <button onClick={() => setSelectedDoc(null)} className="p-1 hover:bg-gray-200 rounded"><X className="w-5 h-5" /></button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatMessages.length === 0 && (
                <div className="text-center text-gray-400 py-8">
                  <MessageSquare className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-sm">Ask a question about this document</p>
                  <p className="text-xs mt-1">e.g. "What are the key terms?" or "Summarize this judgment"</p>
                </div>
              )}
              {chatMessages.map((msg, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex justify-end">
                    <div className="bg-emerald-600 text-white rounded-lg rounded-tr-sm px-3 py-2 text-sm max-w-[80%]">{msg.message}</div>
                  </div>
                  {msg.response && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 rounded-lg rounded-tl-sm px-3 py-2 text-sm max-w-[80%] whitespace-pre-wrap">{msg.response}</div>
                    </div>
                  )}
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg px-3 py-2 text-sm"><Loader2 className="w-4 h-4 animate-spin text-gray-500" /></div>
                </div>
              )}
            </div>

            <div className="p-4 border-t">
              <div className="flex gap-2">
                <input type="text" value={chatInput} onChange={e => setChatInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendChatMessage()} placeholder="Ask about this document..." className="flex-1 px-3 py-2 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400" />
                <button onClick={sendChatMessage} disabled={chatLoading || !chatInput.trim()} className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50"><Send className="w-4 h-4" /></button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
