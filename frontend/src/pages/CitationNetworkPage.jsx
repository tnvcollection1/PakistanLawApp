import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { getCitationNetwork } from '@/services/citationService';

const CitationNetworkPage = () => {
  const [network, setNetwork] = useState({ nodes: [], edges: [] });

  useEffect(() => {
    getCitationNetwork().then(setNetwork);
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Citation Network</h1>
      <div className="border rounded p-4 mb-4">
        <svg viewBox="0 0 800 400" className="w-full h-64">
          {network.edges?.map((edge, i) => (
            <line
              key={i}
              x1={network.nodes[edge.source]?.x || 0}
              y1={network.nodes[edge.source]?.y || 0}
              x2={network.nodes[edge.target]?.x || 0}
              y2={network.nodes[edge.target]?.y || 0}
              stroke="#999"
              strokeWidth="1"
            />
          ))}
          {network.nodes?.map((node, i) => (
            <circle key={i} cx={node.x} cy={node.y} r={5} fill="#333" />
          ))}
        </svg>
      </div>
      <div className="space-y-2">
        {network.nodes?.map((node, i) => (
          <Card key={i} className="p-2">
            <p className="font-bold">{node.label}</p>
            <p className="text-sm text-muted-foreground">Citations: {node.citations || 0}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default CitationNetworkPage;
