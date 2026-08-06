import React from 'react';
import { Link } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';

const ReferenceLink = ({ reference, className = '' }) => {
  if (!reference) return null;

  const { type, id, title, url } = reference;

  // Internal link for cases and statutes
  if (type === 'case') {
    return (
      <Link
        to={`/case/${id}`}
        className={`inline-flex items-center text-blue-600 hover:text-blue-800 hover:underline ${className}`}
      >
        {title || `Case ${id}`}
      </Link>
    );
  }

  if (type === 'statute') {
    return (
      <Link
        to={`/statute/${id}`}
        className={`inline-flex items-center text-blue-600 hover:text-blue-800 hover:underline ${className}`}
      >
        {title || `Statute ${id}`}
      </Link>
    );
  }

  // External link
  if (url) {
    return (
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className={`inline-flex items-center text-blue-600 hover:text-blue-800 hover:underline ${className}`}
      >
        {title || url}
        <ExternalLink className="w-3 h-3 ml-1" />
      </a>
    );
  }

  return <span className={className}>{title || 'Unknown Reference'}</span>;
};

export default ReferenceLink;
