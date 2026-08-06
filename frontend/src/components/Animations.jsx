import React, { useState, useEffect } from 'react';

export default function Animations() {
  return (
    <style>{`
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      .animate-fadeIn {
        animation: fadeIn 0.3s ease-in;
      }
    `}</style>
  );
}
