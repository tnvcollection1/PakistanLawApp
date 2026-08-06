import React from 'react';

export default function MainContent({ children }) {
  return (
    <main className="flex-1 overflow-auto p-4">
      <div className="mx-auto max-w-7xl">
        {children}
      </div>
    </main>
  );
}
