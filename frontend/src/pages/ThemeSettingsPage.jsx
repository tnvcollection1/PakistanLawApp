import React, { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Palette, ChevronLeft, Moon, Sun, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/context/ThemeContext";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";

export default function ThemeSettingsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { theme, themeId, setTheme, themes, darkMode, toggleDarkMode } = useTheme();
  const navigate = useNavigate();

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Theme Settings" onMenuClick={() => setSidebarOpen(true)} />

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
                  <h1 className="text-2xl font-bold text-white">Theme Settings</h1>
                  <p className="text-slate-400 text-sm">Customize your interface appearance</p>
                </div>
              </div>
            </div>

            {/* Dark Mode Toggle */}
            <div className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-5 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {darkMode ? (
                    <Moon className="w-5 h-5 text-indigo-400" />
                  ) : (
                    <Sun className="w-5 h-5 text-amber-400" />
                  )}
                  <div>
                    <h3 className="text-white font-medium">Dark Mode</h3>
                    <p className="text-slate-400 text-sm">Toggle between light and dark themes</p>
                  </div>
                </div>
                <Button
                  variant={darkMode ? "default" : "outline"}
                  onClick={toggleDarkMode}
                  className={darkMode ? "bg-indigo-600" : ""}
                >
                  {darkMode ? "On" : "Off"}
                </Button>
              </div>
            </div>

            {/* Theme Selection */}
            <h3 className="text-white font-semibold mb-4">Select Theme</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.values(themes).map((t) => (
                <motion.button
                  key={t.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setTheme(t.id)}
                  className={`rounded-xl border p-4 text-left transition-all ${
                    themeId === t.id
                      ? "border-pink-500 bg-pink-500/10"
                      : "border-slate-700/50 bg-slate-800/40 hover:bg-slate-800/60"
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-white font-medium">{t.name}</span>
                    {themeId === t.id && (
                      <Check className="w-4 h-4 text-pink-400" />
                    )}
                  </div>
                  <p className="text-slate-400 text-sm mb-2">{t.desc}</p>
                  <div className="flex items-center gap-2">
                    <div
                      className="w-6 h-6 rounded-full"
                      style={{ backgroundColor: t.primary }}
                    />
                    <div
                      className="w-6 h-6 rounded-full"
                      style={{ backgroundColor: t.accent }}
                    />
                    <span className="text-slate-500 text-xs ml-auto">{t.rank}</span>
                  </div>
                </motion.button>
              ))}
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
