import { useState, useCallback, useMemo } from "react";
import type { ChatMessage, UserMemory } from "@/lib/types";
import { sendMessage } from "@/lib/chatApi";
import { extractMemory } from "@/lib/memoryExtractor";
import { getStableUserId } from "@/lib/userId";
import MemoryPanel from "./MemoryPanel";
import ChatWindow from "./ChatWindow";
import ToolResultPanel from "./ToolResultPanel";
import { Bot, PanelLeftClose, PanelRightClose } from "lucide-react";

export default function AppShell() {
  const userId = useMemo(() => getStableUserId(), []);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [memory, setMemory] = useState<UserMemory>({});
  const [latestResult, setLatestResult] = useState<{ toolUsed: string | null; result: unknown }>({
    toolUsed: null,
    result: null,
  });
  const [loading, setLoading] = useState(false);
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);

  const handleSend = useCallback(
    async (text: string) => {
      const userMsg: ChatMessage = { role: "user", content: text };
      setMessages((prev) => [...prev, userMsg]);
      setMemory((prev) => extractMemory(text, prev));

      setLoading(true);

      try {
        const res = await sendMessage({ user_id: userId, message: text });

        const assistantMsg: ChatMessage = {
          role: "assistant",
          content: res.assistantText,
          toolUsed: res.toolUsed,
          result: res.result,
        };

        setMessages((prev) => [...prev, assistantMsg]);

        if (res.result != null) {
          setLatestResult({ toolUsed: res.toolUsed, result: res.result });
        }
      } catch (err) {
        const detail = err instanceof Error ? err.message : "Request failed";
        const assistantMsg: ChatMessage = {
          role: "assistant",
          content: `**Error:** ${detail}`,
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } finally {
        setLoading(false);
      }
    },
    [userId]
  );

  return (
    <div className="h-screen flex flex-col agent-gradient-bg">
      <header className="h-14 border-b bg-card/80 backdrop-blur-md flex items-center px-4 gap-3 shrink-0" role="banner">
        <button
          onClick={() => setLeftOpen((p) => !p)}
          className="lg:hidden text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-secondary"
          aria-label="Toggle left panel"
        >
          <PanelLeftClose className="h-4 w-4" />
        </button>
        <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center shadow-sm">
          <Bot className="h-4 w-4 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight">Agent Chat</h1>
          <p className="text-[10px] text-muted-foreground font-mono leading-none">+ memory</p>
        </div>
        <span className="text-xs text-muted-foreground font-mono ml-auto hidden sm:flex items-center gap-1.5 max-w-[min(40vw,14rem)] truncate" title={userId}>
          <span className="h-1.5 w-1.5 rounded-full bg-accent shrink-0" />
          {userId}
        </span>
        <button
          onClick={() => setRightOpen((p) => !p)}
          className="lg:hidden text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-secondary"
          aria-label="Toggle right panel"
        >
          <PanelRightClose className="h-4 w-4" />
        </button>
      </header>

      <div className="flex flex-1 min-h-0">
        <aside
          className={`${
            leftOpen ? "w-64" : "w-0"
          } transition-all duration-200 overflow-hidden border-r bg-card/60 backdrop-blur-sm shrink-0`}
          role="complementary"
          aria-label="Memory panel"
        >
          <div className="p-4 space-y-6 w-64">
            <MemoryPanel memory={memory} />
          </div>
        </aside>

        <main className="flex-1 min-w-0" role="main" aria-label="Chat conversation">
          <ChatWindow messages={messages} onSend={handleSend} loading={loading} />
        </main>

        <aside
          className={`${
            rightOpen ? "w-80" : "w-0"
          } transition-all duration-200 overflow-hidden border-l bg-card/60 backdrop-blur-sm shrink-0`}
          role="complementary"
          aria-label="Tool results panel"
        >
          <div className="w-80 h-full">
            <ToolResultPanel toolUsed={latestResult.toolUsed} result={latestResult.result} />
          </div>
        </aside>
      </div>
    </div>
  );
}
