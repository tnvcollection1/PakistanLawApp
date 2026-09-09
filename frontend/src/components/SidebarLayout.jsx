import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Home, Search, BookOpen, Scale, Building2, BookMarked, Menu, X, Bot, Sparkles } from "lucide-react";

const NAV_ITEMS = [
  { path: "/", label: "Home", icon: Home },
  { path: "/lawbot", label: "LawBot AI", icon: Bot, highlight: true },
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
        className={`fixed left-0 top-0 h-full w-64 bg-[#1a365d] text-white z-50 transition-transform duration-300 ease-in-out
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
          md:translate-x-0 md:static md:z-auto`}
      >
        <div className="p-6">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Scale size={24} className="text-[#c9a227]" />
            Pakistan Law App
          </h1>
        </div>

        <nav className="px-4 pb-4">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors
                  ${isActive ? "bg-[#c9a227] text-[#1a365d] font-semibold" : "hover:bg-white/10"}
                  ${item.highlight && !isActive ? "bg-[#c9a227]/20 text-[#c9a227] hover:bg-[#c9a227]/30" : ""}`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
                {item.highlight && (
                  <Sparkles size={12} className="ml-auto text-[#c9a227]" />
                )}
              </Link>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 overflow-y-auto min-w-0">
        {children}
      </main>
    </div>
  );
}
