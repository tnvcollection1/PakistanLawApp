import React, { useState, useRef } from "react";
import { BookOpen, Scale, Gavel, Building2, ScrollText } from "lucide-react";

const TYPE_STYLES = {
  section:   "text-red-700 border-b border-red-300 hover:bg-red-50",
  case:      "text-blue-700 border-b border-blue-300 hover:bg-blue-50",
  term:      "text-green-700 border-b border-dashed border-green-400 hover:bg-green-50",
  court:     "text-amber-700 border-b border-amber-300 hover:bg-amber-50",
  article:   "text-purple-700 border-b border-purple-300 hover:bg-purple-50",
};

const TYPE_ICONS = {
  section: BookOpen, case: Scale, term: Gavel, court: Building2, article: ScrollText,
};

export default function ReferenceLink({ type, text, data, onClick }) {
  const [tooltip, setTooltip] = useState(null);
  const [loading, setLoading] = useState(false);
  const timerRef = useRef(null);
  const style = TYPE_STYLES[type] || TYPE_STYLES.term;
  const Icon = TYPE_ICONS[type] || Gavel;

  const handleMouseEnter = () => {
    timerRef.current = setTimeout(() => {
      setLoading(true);
      fetchPreview().then(p => { setTooltip(p); setLoading(false); }).catch(() => setLoading(false));
    }, 300);
  };

  const handleMouseLeave = () => {
    clearTimeout(timerRef.current);
    setTooltip(null);
  };

  const fetchPreview = async () => {
    const API = process.env.REACT_APP_API_URL || "/api";
    if (type === "section") {
      return { title: `Section ${data?.section} ${data?.act}`, body: "Click to view section details and related cases" };
    } else if (type === "case") {
      return { title: data?.citation || text, body: "Click to view this case" };
    } else if (type === "term") {
      return { title: data?.term || text, body: "Click for Black's Law definition" };
    } else if (type === "court") {
      return { title: data?.court || text, body: "Click to browse cases from this court" };
    }
    return { title: text, body: "Click to learn more" };
  };

  return (
    <span className="relative inline">
      <span
        className={`${style} cursor-pointer transition-colors duration-150 rounded px-0.5`}
        onClick={() => onClick && onClick({ type, text, data })}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {text}
      </span>
      {tooltip && (
        <span className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 bg-gray-900 text-white text-xs rounded-lg py-2 px-3 shadow-xl pointer-events-none">
          <span className="font-semibold flex items-center gap-1"><Icon size={12}/> {tooltip.title}</span>
          <span className="text-gray-300 mt-1 block">{tooltip.body}</span>
          <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900"/>
        </span>
      )}
    </span>
  );
}
