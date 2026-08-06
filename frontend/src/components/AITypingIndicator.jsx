import React from 'react';

export default function AITypingIndicator() {
  return (
    <div className="flex items-center gap-1 text-muted-foreground animate-pulse">
      <span>AI is thinking</span>
      <span className="animate-bounce">.</span>
      <span className="animate-bounce delay-100">.</span>
      <span className="animate-bounce delay-200">.</span>
    </div>
  );
}
