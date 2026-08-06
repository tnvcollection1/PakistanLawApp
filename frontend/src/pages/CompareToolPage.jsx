import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";

export default function CompareToolPage() {
  const [text1, setText1] = useState("");
  const [text2, setText2] = useState("");
  const [differences, setDifferences] = useState([]);

  const handleCompare = () => {
    // Simple comparison (placeholder)
    const words1 = text1.split(/\s+/);
    const words2 = text2.split(/\s+/);
    const diff = [];
    for (let i = 0; i < Math.max(words1.length, words2.length); i++) {
      if (words1[i] !== words2[i]) {
        diff.push({
          position: i,
          word1: words1[i] || "",
          word2: words2[i] || "",
        });
      }
    }
    setDifferences(diff.slice(0, 20)); // Show first 20 differences
    toast.success(`Found ${diff.length} differences`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Compare Tool</h1>
      <p className="text-muted-foreground mb-6">
        Compare two texts side by side to find differences.
      </p>
      <Separator className="my-6" />
      <div className="grid gap-6 md:grid-cols-2 mb-6">
        <div>
          <label className="text-sm font-medium mb-2 block">Text 1</label>
          <Textarea
            value={text1}
            onChange={(e) => setText1(e.target.value)}
            placeholder="Paste first text here..."
            className="h-64"
          />
        </div>
        <div>
          <label className="text-sm font-medium mb-2 block">Text 2</label>
          <Textarea
            value={text2}
            onChange={(e) => setText2(e.target.value)}
            placeholder="Paste second text here..."
            className="h-64"
          />
        </div>
      </div>
      <Button onClick={handleCompare} className="mb-6">
        Compare
      </Button>
      {differences.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold">Differences</h2>
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted">
                <tr>
                  <th className="px-4 py-2 text-left">Position</th>
                  <th className="px-4 py-2 text-left">Text 1</th>
                  <th className="px-4 py-2 text-left">Text 2</th>
                </tr>
              </thead>
              <tbody>
                {differences.map((d, i) => (
                  <tr key={i} className="border-t">
                    <td className="px-4 py-2">{d.position}</td>
                    <td className="px-4 py-2 text-red-600">{d.word1}</td>
                    <td className="px-4 py-2 text-green-600">{d.word2}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
