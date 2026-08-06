import React, { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Palette, ChevronLeft, Check, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/context/ThemeContext";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";

export default function ThemePreview() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { theme, themeId, setTheme, themes, darkMode, toggleDarkMode } = useTheme();
  const [previewTheme, setPreviewTheme] = useState(themeId);
  const navigate = useNavigate();

  const preview = themes[previewTheme] || themes.latham;

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Theme Preview" onMenuClick={() => setSidebarOpen(true)} />

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
                <div className="w-10 h-10 rounded-lg bg-pink-500/20 flex items-center justify-center">
                  <Palette className="w-5 h-5 text-pink-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Theme Preview</h1>
                  <p className="text-slate-400 text-sm">Preview themes before applying</p>
                </div>
              </div>
            </div>

            {/* Theme selector */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
              {Object.values(themes).map((t) => (
                <button
                  key={t.id}
                  onClick={() => setPreviewTheme(t.id)}
                  className={`rounded-xl border p-3 text-left transition-all ${
                    previewTheme === t.id ? 'border-pink-500 bg-pink-500/10' : 'border-slate-700/50 bg-slate-800/40'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white text-sm font-medium">{t.name}</span>
                    {previewTheme === t.id && <Check className="w-3 h-3 text-pink-400" />}
                  </div>
                  <div className="flex gap-1.5">
                    <div className="w-5 h-5 rounded-full" style={{ backgroundColor: t.primary }} />
                    <div className="w-5 h-5 rounded-full" style={{ backgroundColor: t.accent }} />
                    <div className="w-5 h-5 rounded-full" style={{ backgroundColor: t.bg }} />
                  </div>
                </button>
              ))}
            </div>

            {/* Preview panel */}
            <div
              className="rounded-xl border p-6 transition-colors"
              style={{
                backgroundColor: preview.bg,
                borderColor: preview.border,
                color: preview.text,
                fontFamily: preview.fontBody,
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 style={{ fontFamily: preview.fontHeading, fontSize: '1.5rem', fontWeight: 'bold' }}>
                  Preview: {preview.name}
                </h2>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    style={{ backgroundColor: preview.buttonBg, color: preview.buttonText }}
                    onClick={() => setTheme(previewTheme)}
                  >
                    Apply Theme
                  </Button>
                </div>
              </div>

              <div
                className="rounded-lg p-4 mb-4"
                style={{ backgroundColor: preview.card, boxShadow: preview.cardShadow }}
              >
                <h3 style={{ color: preview.text, fontWeight: 600 }}>Sample Card</h3>
                <p style={{ color: preview.textSecondary }}>
                  This is how cards and content will appear with the {preview.name} theme.
                </p>
                <div className="flex gap-2 mt-3">
                  <span
                    className="px-2 py-1 rounded-full text-xs"
                    style={{ backgroundColor: preview.tagBg, color: preview.tagText }}
                  >
                    Tag Example
                  </span>
                  <span
                    className="px-2 py-1 rounded-full text-xs"
                    style={{ backgroundColor: preview.accentLight, color: preview.accent }}
                  >
                    Active
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: preview.accentLight }}
                >
                  <Palette className="w-5 h-5" style={{ color: preview.accent }} />
                </div>
                <div>
                  <p style={{ color: preview.text, fontWeight: 500 }}>Theme Details</p>
                  <p style={{ color: preview.textSecondary, fontSize: '0.875rem' }}>
                    {preview.desc} — {preview.rank}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
