import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function StatuteCasesPage() {
  const { statuteId } = useParams();
  const [cases, setCases] = useState([]);
  const [statute, setStatute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetch(`/api/statutes/${statuteId}`)
      .then((res) => res.json())
      .then((data) => {
        setStatute(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [statuteId]);

  useEffect(() => {
    fetch(`/api/statutes/${statuteId}/cases?page=${page}`)
      .then((res) => res.json())
      .then((data) => {
        setCases(data.cases || []);
      });
  }, [statuteId, page]);

  if (loading) return <div className="p-6">Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">{statute?.title}</h1>
      <p className="text-gray-500 mb-6">Year: {statute?.year}</p>
      <h2 className="text-xl font-semibold mb-4">Cases Interpreting this Statute</h2>
      <div className="space-y-3">
        {cases.map((c) => (
          <Card key={c.id}>
            <CardContent className="p-4">
              <Link to={`/cases/${c.id}`} className="text-blue-600 hover:underline font-medium">
                {c.title}
              </Link>
              <div className="text-sm text-gray-500">{c.citation}</div>
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="flex justify-between mt-4">
        <Button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
        <Button onClick={() => setPage(p => p + 1)}>Next</Button>
      </div>
    </div>
  );
}
