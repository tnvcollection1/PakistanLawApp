import React, { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { FileText, ChevronLeft, Upload, Loader2, AlertCircle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function DocumentAnalyzerPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
      setResult(null);
    }
  };

  const analyzeDocument = async () => {
    if (!file) return;
    setAnalyzing(true);
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const res = await api.post("/analyze-document", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setResult(res.data);
    } catch (err) {
      setResult({ error: "Analysis failed. Please try again." });
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Document Analyzer" onMenuClick={() => setSidebarOpen(true)} />

        <div className="p-6 overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <div className="flex items-center gap-4 mb-6">
              <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                <ChevronLeft className="w-5 h-5 text-slate-300" />
              </Button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-indigo-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Document Analyzer</h1>
                  <p className="text-slate-400 text-sm">Upload and analyze legal documents</p>
                </div>
              </div>
            </div>

            {/* Upload Area */}
            <div className="rounded-xl border-2 border-dashed border-slate-700/50 bg-slate-800/20 p-8 text-center mb-6 hover:border-slate-600 transition-colors">
              <Upload className="w-10 h-10 text-slate-500 mx-auto mb-3" />
              <p className="text-slate-400 mb-2">Drag and drop a document, or click to browse</p>
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileChange}
                className="hidden"
                id="doc-upload"
              />
              <label htmlFor="doc-upload">
                <Button variant="outline" className="cursor-pointer" asChild>
                  <span>Choose File</span>
                </Button>
              </label>
              {file && (
                <p className="text-slate-300 text-sm mt-3">Selected: {file.name}</p>
              )}
            </div>

            {file && (
              <Button
                className="bg-indigo-600 hover:bg-indigo-700 w-full mb-6"
                onClick={analyzeDocument}
                disabled={analyzing}
              >
                {analyzing ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <FileText className="w-4 h-4 mr-2" />
                )}
                {analyzing ? "Analyzing..." : "Analyze Document"}
              </Button>
            )}

            {/* Results */}
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                {result.error ? (
                  <div className="rounded-xl border border-red-700/50 bg-red-900/20 p-4 flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-red-400" />
                    <p className="text-red-300">{result.error}</p>
                  </div>
                ) : (
                  <>
                    <div className="rounded-xl border border-green-700/50 bg-green-900/20 p-4 flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-green-400" />
                      <p className="text-green-300">Analysis complete</p>
                    </div>
                    
                    {result.summary && (
                      <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
                        <h3 className="text-white font-semibold mb-3">Summary</h3>
                        <p className="text-slate-300 text-sm">{result.summary}</p>
                      </div>
                    )}
                    
                    {result.key_points?.length > 0 && (
                      <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
                        <h3 className="text-white font-semibold mb-3">Key Points</h3>
                        <ul className="space-y-2">
                          {result.key_points.map((point, idx) => (
                            <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                              <span className="text-indigo-400 mt-1">•</span>
                              {point}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {result.entities?.length > 0 && (
                      <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5">
                        <h3 className="text-white font-semibold mb-3">Named Entities</h3>
                        <div className="flex flex-wrap gap-2">
                          {result.entities.map((entity, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs"
                            >
                              {entity}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </motion.div>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
