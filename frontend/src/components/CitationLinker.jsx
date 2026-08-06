import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

export default function CitationLinker() {
  const [citation, setCitation] = useState("");
  const [links, setLinks] = useState([]);

  const handleSearch = () => {
    // Mock citation linking
    setLinks([
      { id: 1, case: "Case A", relation: "Cited" },
      { id: 2, case: "Case B", relation: "Distinguished" },
      { id: 3, case: "Case C", relation: "Followed" },
    ]);
  };

  return (
    <div className="p-4 border rounded-lg bg-background">
      <h2 className="text-lg font-semibold mb-4">Citation Linker</h2>
      <div className="flex space-x-2 mb-4">
        <Input
          placeholder="Enter citation..."
          value={citation}
          onChange={(e) => setCitation(e.target.value)}
        />
        <Button onClick={handleSearch}>Find Links</Button>
      </div>
      {links.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium">Linked Cases</h3>
          <ul className="space-y-2">
            {links.map((link) => (
              <li key={link.id} className="flex justify-between items-center p-2 rounded bg-muted">
                <span>{link.case}</span>
                <span className="text-sm text-muted-foreground">{link.relation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
