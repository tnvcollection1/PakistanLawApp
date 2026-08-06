import React from 'react';

export default function ChatMessage({ message, isUser }) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-lg px-4 py-2 ${isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
        <p>{message.text}</p>
      </div>
    </div>
  );
}
