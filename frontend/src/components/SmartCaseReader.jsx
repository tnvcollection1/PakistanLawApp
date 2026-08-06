import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { BookOpen, ChevronLeft, ChevronRight, Highlighter, Bookmark, Share2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function SmartCaseReader({ caseData, onClose }) {
  const [currentPage, setCurrentPage] = useState(0);
  const [highlights, setHighlights] = useState([]);
  const [bookmarks, setBookmarks] = useState([]);
  const [selectedText, setSelectedText] = useState("");

  const pages = caseData?.pages || [caseData?.full_text || caseData?.headnote || "No content available."];

  const handleHighlight = () => {
    const selection = window.getSelection().toString();
    if (selection) {
      setHighlights(prev => [...prev, { text: selection, page: currentPage }]);
    }
  };

  const handleBookmark = () => {
    setBookmarks(prev => [...prev, { page: currentPage, timestamp: new Date().toISOString() }]);
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="fixed inset-0 z-50 bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B] flex flex-col"
    >
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={onClose}>
            <ChevronLeft className="w-5 h-5 text-slate-300" />
          </Button>
          <h2 className="text-white font-semibold truncate max-w-md">
            {caseData?.title || "Case Reader"}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={handleHighlight} className="text-amber-400">
            <Highlighter className="w-4 h-4 mr-1" /> Highlight
          </Button>
          <Button variant="ghost" size="sm" onClick={handleBookmark} className="text-sky-400">
            <Bookmark className="w-4 h-4 mr-1" /> Bookmark
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto bg-slate-800/30 rounded-xl p-6 border border-slate-700/50">
          <div className="prose prose-invert max-w-none">
            {pages[currentPage]?.split("\n").map((paragraph, idx) => (
              <p key={idx} className="text-slate-300 leading-relaxed mb-4">
                {paragraph}
              </p>
            ))}
          </div>
        </div>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between p-4 border-t border-slate-700/50">
        <Button
          variant="outline"
          size="sm"
          disabled={currentPage <= 0}
          onClick={() => setCurrentPage(p => p - 1)}
        >
          <ChevronLeft className="w-4 h-4 mr-1" /> Previous
        </Button>
        <span className="text-slate-400 text-sm">
          Page {currentPage + 1} of {pages.length}
        </span>
        <Button
          variant="outline"
          size="sm"
          disabled={currentPage >= pages.length - 1}
          onClick={() => setCurrentPage(p => p + 1)}
        >
          Next <ChevronRight className="w-4 h-4 ml-1" />
        </Button>
      </div>
    </motion.div>
  );
}
