import React from 'react';
import { Link } from 'react-router-dom';

export default function Navigation() {
  return (
    <nav className="bg-primary text-primary-foreground p-4">
      <div className="mx-auto max-w-7xl flex justify-between">
        <Link to="/" className="font-bold text-lg">PakistanLaw</Link>
        <div className="space-x-4">
          <Link to="/search">Search</Link>
          <Link to="/statutes">Statutes</Link>
          <Link to="/judgments">Judgments</Link>
          <Link to="/words-phrases">Words & Phrases</Link>
        </div>
      </div>
    </nav>
  );
}
