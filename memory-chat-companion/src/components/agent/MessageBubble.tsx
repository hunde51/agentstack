import type { ChatMessage } from "@/lib/types";
import { Bot, UserIcon, Wrench } from "lucide-react";

interface Props {
  message: ChatMessage;
  index: number;
}

export default function MessageBubble({ message, index }: Props) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex gap-2.5 animate-msg-in ${isUser ? "flex-row-reverse" : ""}`}
      style={{ animationDelay: `${index * 60}ms` }}
      role="log"
      aria-label={`${isUser ? "You" : "Assistant"} said: ${message.content.replace(/\*\*/g, "")}`}
    >
      <div
        className={`shrink-0 h-7 w-7 rounded-full flex items-center justify-center text-xs shadow-sm ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-card text-foreground border"
        }`}
        aria-hidden
      >
        {isUser ? <UserIcon className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
      </div>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm ${
          isUser
            ? "bg-primary text-primary-foreground rounded-tr-md"
            : "bg-card text-card-foreground border rounded-tl-md"
        }`}
      >
        <span
          dangerouslySetInnerHTML={{
            __html: message.content.replace(
              /\*\*(.*?)\*\*/g,
              '<strong class="font-semibold">$1</strong>'
            ),
          }}
        />
        {message.toolUsed && (
          <span className="flex items-center gap-1 mt-1.5 text-xs opacity-70 font-mono">
            <Wrench className="h-3 w-3" />
            {message.toolUsed}
          </span>
        )}
      </div>
    </div>
  );
}
