import React from 'react';
import { Link } from 'react-router-dom';

export default function ReferenceLink({ reference }) {
  return (
    <Link
      to={`/judgment/${reference.id}`}
      className="text-primary hover:underline"
    >
      {reference.citation}
    </Link>
  );
}
