import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Home, Search, BookOpen, Scale, Building2, BookMarked, Menu, X, Bot, Sparkles, FileText, Calendar, FolderOpen, BookOpen as NotebookIcon } from "lucide-react";

const NAV_ITEMS = [
  { path: "/", label: "Home", icon: Home },
  { path: "/lawbot", label: "LawBot AI", icon: Bot, highlight: true },
];

const LAWYER_TOOLS = [
  { path: "/drafter", label: "Legal Drafter", icon: FileText },
  { path: "/diary", label: "Case Diary", icon: Calendar },
  { path: "/vault", label: "Document Vault", icon: FolderOpen },
  { path: "/notebook", label: "Research Notebook", icon: NotebookIcon },
];

const RESEARCH_ITEMS = [
  { path: "/citation-search", label: "Citation Search", icon: Search },
  { path: "/cases", label: "Cases", icon: BookOpen },
  { path: "/courts", label: "Courts", icon: Scale },
  { path: "/laws", label: "Laws", icon: BookMarked },
  { path: "/journals", label: "Journals", icon: Building2 },
];

export default function SidebarLayout({ children }) {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setIsOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === "Escape") setIsOpen(false);
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, []);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [isOpen]);

  const isActive = (path) => location.pathname === path;

  return (
    <div className="flex h-screen bg-gray-50">
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md md:hidden"
        aria-label="Toggle menu"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      <aside
        className={`fixed md:sticky top-0 left-0 z-40 h-screen w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="p-5 border-b border-gray-100">
          <Link to="/" className="flex items-center gap-2" onClick={() => setIsOpen(false)}>
            <Scale className="w-6 h-6 text-emerald-700" />
            <span className="text-lg font-bold tracking-tight" style={{ color: 'var(--text-h)' }}>
              PakLaw
            </span>
          </Link>
        </div>

        <nav className="p-3 space-y-1 overflow-y-auto h-[calc(100vh-80px)]">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.path)
                    ? item.highlight
                      ? "bg-amber-50 text-amber-700 border border-amber-200"
                      : "bg-emerald-50 text-emerald-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
                {item.highlight && <Sparkles className="w-3.5 h-3.5 ml-auto text-amber-500" />}
              </Link>
            );
          })}

          <div className="mt-4 mb-1">
            <p className="px-3 text-[10px] font-bold text-gray-400 uppercase tracking-wider">
              Lawyer Tools
            </p>
          </div>
          {LAWYER_TOOLS.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.path)
                    ? "bg-emerald-50 text-emerald-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            );
          })}

          <div className="mt-4 mb-1">
            <p className="px-3 text-[10px] font-bold text-gray-400 uppercase tracking-wider">
              Research
            </p>
          </div>
          {RESEARCH_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.path)
                    ? "bg-emerald-50 text-emerald-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 min-w-0 overflow-y-auto md:ml-0">
        <div className="md:hidden h-14" />
        {children}
      </main>
    </div>
  );
}
