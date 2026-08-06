import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";

export default function CitatorPanel() {
  const [citation, setCitation] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = () => {
    // Mock results
    setResults([
      { id: 1, case: "Case A", treatment: "Cited" },
      { id: 2, case: "Case B", treatment: "Distinguished" },
      { id: 3, case: "Case C", treatment: "Followed" },
    ]);
  };

  return (
    <div className="p-4 border rounded-lg bg-background">
      <h2 className="text-lg font-semibold mb-4">Citator</h2>
      <div className="flex space-x-2 mb-4">
        <Input
          placeholder="Enter citation..."
          value={citation}
          onChange={(e) => setCitation(e.target.value)}
        />
        <Button onClick={handleSearch}>Search</Button>
      </div>
      <Separator className="my-4" />
      {results.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium">Results</h3>
          <ul className="space-y-2">
            {results.map((r) => (
              <li key={r.id} className="flex justify-between items-center p-2 rounded bg-muted">
                <span>{r.case}</span>
                <span className="text-sm text-muted-foreground">{r.treatment}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
