import { useEffect, useRef } from "react";
import type { ChatMessage } from "@/lib/types";
import MessageBubble from "./MessageBubble";
import Composer from "./Composer";

interface Props {
  messages: ChatMessage[];
  onSend: (text: string) => void;
  loading: boolean;
}

export default function ChatWindow({ messages, onSend, loading }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} index={i} />
        ))}
        {loading && (
          <div className="flex gap-2.5 items-center animate-fade-in">
            <div className="h-7 w-7 rounded-full bg-card border flex items-center justify-center shadow-sm" aria-hidden>
              <span className="flex gap-0.5">
                <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" style={{ animationDelay: "0ms" }} />
                <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" style={{ animationDelay: "150ms" }} />
                <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" style={{ animationDelay: "300ms" }} />
              </span>
            </div>
            <span className="text-xs text-muted-foreground">Thinking…</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="border-t p-3 bg-card/60 backdrop-blur-md sticky bottom-0">
        <Composer onSend={onSend} disabled={loading} />
      </div>
    </div>
  );
}
