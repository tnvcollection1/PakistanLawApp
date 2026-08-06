import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function MostCitedPage() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    fetch(`/api/cases/most-cited?page=${page}`)
      .then((res) => res.json())
      .then((data) => {
        setCases(data.cases || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [page]);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Most Cited Cases</h1>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="space-y-4">
          {cases.map((c) => (
            <Card key={c.id}>
              <CardContent className="p-4 flex justify-between items-center">
                <div>
                  <Link to={`/cases/${c.id}`} className="text-blue-600 hover:underline font-medium">
                    {c.title}
                  </Link>
                  <div className="text-sm text-gray-500">{c.citation}</div>
                </div>
                <div className="text-sm font-semibold">{c.citation_count} citations</div>
              </CardContent>
            </Card>
          ))}
          <div className="flex justify-between mt-4">
            <Button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
            <Button onClick={() => setPage(p => p + 1)}>Next</Button>
          </div>
        </div>
      )}
    </div>
  );
}
