import React from 'react';

export default function ChatMessage({ message, isUser }) {
  return (
    <div className={`p-3 rounded-lg ${isUser ? 'bg-blue-100 ml-auto' : 'bg-gray-100'} max-w-[80%]`}>
      <p className="text-sm">{message}</p>
    </div>
  );
}
