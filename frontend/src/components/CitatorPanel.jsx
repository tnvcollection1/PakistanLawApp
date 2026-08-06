import React, { useState, useEffect } from 'react';

const CitatorPanel = ({ caseId }) => {
  const [citations, setCitations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCitations = async () => {
      try {
        const response = await fetch(`/api/cases/${caseId}/citations`);
        const data = await response.json();
        setCitations(data.citations || []);
      } catch (error) {
        console.error('Error fetching citations:', error);
      } finally {
        setLoading(false);
      }
    };

    if (caseId) {
      fetchCitations();
    }
  }, [caseId]);

  if (loading) return <div className="p-4">Loading citations...</div>;

  return (
    <div className="bg-white border rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Cited By</h3>
      {citations.length === 0 ? (
        <p className="text-gray-500">No citations found</p>
      ) : (
        <ul className="space-y-2">
          {citations.map((citation, index) => (
            <li key={index} className="border-b pb-2">
              <a href={citation.url} className="text-blue-600 hover:underline">
                {citation.title}
              </a>
              <p className="text-sm text-gray-500">{citation.citation}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default CitatorPanel;
