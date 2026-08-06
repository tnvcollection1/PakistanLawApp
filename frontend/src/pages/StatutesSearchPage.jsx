import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

export default function StatutesSearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = () => {
    // Mock results
    setResults([
      { id: 1, title: "Pakistan Penal Code", section: "Section 302" },
      { id: 2, title: "Constitution of Pakistan", section: "Article 25" },
      { id: 3, title: "Code of Criminal Procedure", section: "Section 497" },
    ]);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Statute Search</h1>
      <div className="flex space-x-2 mb-6">
        <Input
          placeholder="Search statutes..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="max-w-md"
        />
        <Button onClick={handleSearch}>
          <Search className="mr-2 h-4 w-4" />
          Search
        </Button>
      </div>
      <div className="space-y-4">
        {results.map((result) => (
          <div key={result.id} className="p-4 rounded-lg border">
            <h2 className="text-lg font-semibold">{result.title}</h2>
            <p className="text-sm text-muted-foreground">{result.section}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
