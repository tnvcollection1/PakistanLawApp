import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";

function CitationLinker({ text }) {
  const [linkedText, setLinkedText] = useState(text);

  useEffect(() => {
    if (!text) return;
    // Simple regex to find citations like 2023 SCMR 123 or PLD 2023 SC 1
    const citationRegex = /\b(\d{4}\s+\w+\s+\d+|PLD\s+\d{4}\s+\w+\s+\d+)\b/g;
    let parts = [];
    let lastIndex = 0;
    let match;
    while ((match = citationRegex.exec(text)) !== null) {
      parts.push(text.slice(lastIndex, match.index));
      parts.push(
        <Link key={match.index} to={`/cases?citation=${encodeURIComponent(match[0])}`} className="text-blue-600 hover:underline">
          {match[0]}
        </Link>
      );
      lastIndex = match.index + match[0].length;
    }
    parts.push(text.slice(lastIndex));
    setLinkedText(parts);
  }, [text]);

  return <span>{linkedText}</span>;
}

export default CitationLinker;
