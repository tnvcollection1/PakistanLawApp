import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CompareToolPage() {
  const [text1, setText1] = useState("");
  const [text2, setText2] = useState("");
  const [diff, setDiff] = useState([]);

  const computeDiff = () => {
    const words1 = text1.split(/\s+/);
    const words2 = text2.split(/\s+/);
    const maxLen = Math.max(words1.length, words2.length);
    const result = [];
    for (let i = 0; i < maxLen; i++) {
      if (words1[i] !== words2[i]) {
        result.push({ index: i, left: words1[i] || "", right: words2[i] || "" });
      }
    }
    setDiff(result);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Compare Tool</h1>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <Textarea placeholder="Paste text 1..." value={text1} onChange={(e) => setText1(e.target.value)} rows={10} />
        <Textarea placeholder="Paste text 2..." value={text2} onChange={(e) => setText2(e.target.value)} rows={10} />
      </div>
      <Button onClick={computeDiff} className="mb-6">Compare</Button>
      {diff.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Differences ({diff.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {diff.map((d, i) => (
                <li key={i} className="flex justify-between border-b py-1">
                  <span className="text-red-600 line-through">{d.left}</span>
                  <span className="text-green-600">{d.right}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
