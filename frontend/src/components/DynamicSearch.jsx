import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

export default function DynamicSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();
  const wrapperRef = useRef(null);

  useEffect(() => {
    const delay = setTimeout(() => {
      if (query.trim().length > 2) {
        fetch(`/api/search?q=${encodeURIComponent(query)}&limit=5`)
          .then((res) => res.json())
          .then((data) => {
            setResults(data.results || []);
            setShowDropdown(true);
          })
          .catch(() => toast.error("Search failed"));
      } else {
        setShowDropdown(false);
      }
    }, 300);
    return () => clearTimeout(delay);
  }, [query]);

  useEffect(() => {
    function handleClickOutside(e) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (caseId) => {
    setShowDropdown(false);
    navigate(`/cases/${caseId}`);
  };

  return (
    <div className="relative w-full max-w-md" ref={wrapperRef}>
      <Input
        placeholder="Search cases, statutes..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => query.trim().length > 2 && setShowDropdown(true)}
      />
      {showDropdown && results.length > 0 && (
        <ul className="absolute z-50 w-full bg-white border rounded-md shadow-lg mt-1 max-h-60 overflow-y-auto">
          {results.map((r) => (
            <li
              key={r.id}
              className="px-4 py-2 hover:bg-gray-100 cursor-pointer text-sm"
              onClick={() => handleSelect(r.id)}
            >
              <div className="font-medium">{r.title}</div>
              <div className="text-xs text-gray-500">{r.citation}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
