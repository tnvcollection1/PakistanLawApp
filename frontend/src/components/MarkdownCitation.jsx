import React from 'react';
import ReactMarkdown from 'react-markdown';
import { useNavigate } from 'react-router-dom';

const JOURNALS = ['PLC\\(CS\\)', 'SCMR', 'PLD', 'CLC', 'YLR', 'MLD', 'PCrLJ', 'PLC', 'PTD', 'CLD', 'GBLR'];
const J = JOURNALS.join('|');
const CN = ['Supreme\\s+Court', 'SC', 'Lahore', 'Sindh', 'Karachi', 'Peshawar', 'Quetta', 'Balochistan', 'Islamabad', 'FSC', 'AJK', 'FC'].join('|');

function buildPattern() {
  const p1 = `(\\d{4})\\s+(${J})\\s+(\\d+)`;
  const p2 = `(${J})\\s+(\\d{4})\\s+(${CN})\\s+(\\d+)`;
  return new RegExp(`(?:${p2})|(?:${p1})`, 'gi');
}

function linkifyCitations(text, navigate) {
  const pattern = buildPattern();
  const parts = [];
  let lastIndex = 0;
  let match;
  let keyIdx = 0;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    const citation = match[0];
    const searchQuery = citation.replace(/\s+/g, ' ');
    parts.push(
      <a
        key={`cite-${keyIdx++}`}
        href="#"
        onClick={(e) => { e.preventDefault(); navigate(`/search?keyword=${encodeURIComponent(searchQuery)}`); }}
        className="text-slate-900 dark:text-slate-100 hover:text-emerald-900 underline decoration-emerald-300 hover:decoration-emerald-600 cursor-pointer font-medium"
      >
        {citation}
      </a>
    );
    lastIndex = pattern.lastIndex;
  }
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }
  return parts.length > 0 ? parts : [text];
}

const MarkdownCitation = ({ content }) => {
  const navigate = useNavigate();

  const renderTextWithCitations = ({ children }) => {
    if (typeof children === 'string') {
      return <>{linkifyCitations(children, navigate)}</>;
    }
    if (Array.isArray(children)) {
      return <>{children.map((child, i) =>
        typeof child === 'string'
          ? <React.Fragment key={i}>{linkifyCitations(child, navigate)}</React.Fragment>
          : child
      )}</>;
    }
    return children;
  };

  return (
    <ReactMarkdown
      components={{
        p: ({ children }) => <p className="mb-3 leading-relaxed">{renderTextWithCitations({ children })}</p>,
        h1: ({ children }) => <h1 className="text-lg font-bold text-slate-800 dark:text-slate-200 mt-4 mb-2">{children}</h1>,
        h2: ({ children }) => <h2 className="text-base font-bold text-slate-800 dark:text-slate-200 mt-4 mb-2">{children}</h2>,
        h3: ({ children }) => <h3 className="text-sm font-bold text-slate-700 dark:text-slate-300 mt-3 mb-1">{children}</h3>,
        ul: ({ children }) => <ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal pl-5 mb-3 space-y-1">{children}</ol>,
        li: ({ children }) => <li className="leading-relaxed">{renderTextWithCitations({ children })}</li>,
        strong: ({ children }) => <strong className="font-semibold text-slate-800 dark:text-slate-200">{children}</strong>,
        em: ({ children }) => <em className="italic">{children}</em>,
        blockquote: ({ children }) => (
          <blockquote className="border-l-3 border-emerald-300 pl-3 my-2 text-slate-600 dark:text-muted-foreground italic">{children}</blockquote>
        ),
        code: ({ children }) => <code className="bg-slate-100 px-1 py-0.5 rounded text-sm">{children}</code>,
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

export default MarkdownCitation;
