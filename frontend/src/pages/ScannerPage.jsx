import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Scan, ChevronLeft, FileText, Loader2, AlertCircle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

export default function ScannerPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [scanResults, setScanResults] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const navigate = useNavigate();

  const runScan = async () => {
    setIsScanning(true);
    try {
      const res = await api.post("/scanner/run");
      setScanResults(res.data);
    } catch (err) {
      setScanResults({ error: "Scan failed" });
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Document Scanner" onMenuClick={() => setSidebarOpen(true)} />

        <div className="p-6 overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <div className="flex items-center gap-4 mb-4">
              <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                <ChevronLeft className="w-5 h-5 text-slate-300" />
              </Button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                  <Scan className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Document Scanner</h1>
                  <p className="text-slate-400 text-sm">Scan and analyze legal documents</p>
                </div>
              </div>
            </div>

            <Button
              className="bg-emerald-600 hover:bg-emerald-700 mb-6"
              onClick={runScan}
              disabled={isScanning}
            >
              {isScanning ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Scan className="w-4 h-4 mr-2" />
              )}
              {isScanning ? "Scanning..." : "Run Document Scan"}
            </Button>
          </motion.div>

          {scanResults && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              {scanResults.error ? (
                <div className="rounded-xl border border-red-700/50 bg-red-900/20 p-4 flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400" />
                  <p className="text-red-300">{scanResults.error}</p>
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4">
                      <div className="text-sm text-slate-400 mb-1">Documents Scanned</div>
                      <div className="text-2xl font-bold text-white">{scanResults.scanned || 0}</div>
                    </div>
                    <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4">
                      <div className="text-sm text-slate-400 mb-1">Issues Found</div>
                      <div className="text-2xl font-bold text-red-400">{scanResults.issues || 0}</div>
                    </div>
                    <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4">
                      <div className="text-sm text-slate-400 mb-1">Clean Documents</div>
                      <div className="text-2xl font-bold text-green-400">{scanResults.clean || 0}</div>
                    </div>
                  </div>

                  {scanResults.details?.map((detail, idx) => (
                    <div
                      key={idx}
                      className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        {detail.status === "ok" ? (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-red-400" />
                        )}
                        <span className="text-white font-medium">{detail.filename}</span>
                      </div>
                      {detail.issues?.map((issue, i) => (
                        <p key={i} className="text-slate-400 text-sm ml-6">{issue}</p>
                      ))}
                    </div>
                  ))}
                </>
              )}
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}
