import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function RelatedCasesPanel({ caseId }) {
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/cases/${caseId}/related`)
      .then((res) => res.json())
      .then((data) => {
        setRelated(data.related || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [caseId]);

  if (loading) return <div className="text-sm text-gray-500">Loading related cases...</div>;
  if (!related.length) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Related Cases</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {related.map((c) => (
            <li key={c.id}>
              <Link to={`/cases/${c.id}`} className="text-blue-600 hover:underline text-sm">
                {c.title}
              </Link>
              <div className="text-xs text-gray-500">{c.citation}</div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
