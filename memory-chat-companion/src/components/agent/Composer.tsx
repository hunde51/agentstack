import { useState, type FormEvent, useRef, useEffect } from "react";
import { SendHorizonal } from "lucide-react";

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export default function Composer({ onSend, disabled }: Props) {
  const [text, setText] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!disabled) inputRef.current?.focus();
  }, [disabled]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  };

  const canSend = text.trim().length > 0 && !disabled;

  return (
    <form onSubmit={handleSubmit} className="flex gap-2" aria-label="Send a message">
      <input
        ref={inputRef}
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask about users or weather…"
        disabled={disabled}
        className="flex-1 rounded-xl border bg-background px-4 py-2.5 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent disabled:opacity-50 transition-shadow"
        aria-label="Message input"
      />
      <button
        type="submit"
        disabled={!canSend}
        className={`shrink-0 rounded-xl px-4 py-2.5 transition-all ${
          canSend
            ? "bg-primary text-primary-foreground hover:opacity-90 shadow-sm active:scale-95"
            : "bg-secondary text-muted-foreground cursor-not-allowed"
        }`}
        aria-label="Send message"
      >
        <SendHorizonal className="h-4 w-4" />
      </button>
    </form>
  );
}
