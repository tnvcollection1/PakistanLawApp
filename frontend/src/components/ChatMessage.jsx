import { Bot, User } from "lucide-react";

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] rounded-xl px-4 py-3 ${isUser ? "bg-[#1a365d] text-white" : "bg-white border border-gray-200 shadow-sm"}`}>
        <div className="flex items-center gap-2 mb-1">
          {isUser ? <User size={14} className="text-[#c9a227]"/> : <Bot size={14} className="text-[#1a365d]"/>}
          <span className="text-xs opacity-60">{isUser ? "You" : "AI"}</span>
        </div>
        <div className="text-sm whitespace-pre-wrap">{message.content}</div>
      </div>
    </div>
  );
}
