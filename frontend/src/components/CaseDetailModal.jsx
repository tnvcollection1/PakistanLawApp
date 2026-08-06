import React, { useState } from 'react';

export default function CaseDetailModal({ caseData, onClose }) {
  if (!caseData) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full mx-4 p-6 max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{caseData.citation || caseData.title}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">×</button>
        </div>
        <p className="text-sm text-gray-600 mb-4">{caseData.court} • {caseData.year}</p>
        <div className="prose max-w-none">
          <p>{caseData.headnotes || caseData.full_content}</p>
        </div>
      </div>
    </div>
  );
}
