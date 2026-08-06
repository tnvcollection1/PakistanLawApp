import React, { useState } from 'react';

export default function CaseNotesPanel() {
  const [notes, setNotes] = useState('');

  const saveNotes = () => {
    localStorage.setItem('caseNotes', notes);
  };

  return (
    <div className="bg-white rounded-lg border p-4">
      <h3 className="font-semibold mb-2">Case Notes</h3>
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Add your notes here..."
        className="w-full border rounded px-3 py-2 h-32"
      />
      <button onClick={saveNotes} className="bg-blue-600 text-white px-4 py-2 rounded mt-2">Save</button>
    </div>
  );
}
