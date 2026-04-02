import { useState, useCallback } from "react";
import type { ChatMessage, DummyUser, UserMemory } from "@/lib/types";
import { sendMessage } from "@/lib/chatApi";
import { extractMemory } from "@/lib/memoryExtractor";
import UserSwitcher from "./UserSwitcher";
import MemoryPanel from "./MemoryPanel";
import ChatWindow from "./ChatWindow";
import ToolResultPanel from "./ToolResultPanel";
import { Bot, PanelLeftClose, PanelRightClose } from "lucide-react";

const USERS: DummyUser[] = [
  { id: "alice-001", label: "alice-001" },
  { id: "bob-002", label: "bob-002" },
  { id: "charlie-003", label: "charlie-003" },
];

const INITIAL_MESSAGE: ChatMessage = {
  role: "assistant",
  content: "Hi. I can choose tools like **get_users** and **get_weather**.",
};

export default function AppShell() {
  const [selectedUser, setSelectedUser] = useState(USERS[0].id);
  const [chats, setChats] = useState<Record<string, ChatMessage[]>>({
    "alice-001": [INITIAL_MESSAGE],
    "bob-002": [INITIAL_MESSAGE],
    "charlie-003": [INITIAL_MESSAGE],
  });
  const [memories, setMemories] = useState<Record<string, UserMemory>>({
    "alice-001": {},
    "bob-002": {},
    "charlie-003": {},
  });
  const [latestResult, setLatestResult] = useState<{ toolUsed: string | null; result: any }>({
    toolUsed: null,
    result: null,
  });
  const [loading, setLoading] = useState(false);
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);

  const currentMessages = chats[selectedUser] ?? [INITIAL_MESSAGE];
  const currentMemory = memories[selectedUser] ?? {};

  const handleSend = useCallback(
    async (text: string) => {
      const userMsg: ChatMessage = { role: "user", content: text };
      setChats((prev) => ({
        ...prev,
        [selectedUser]: [...(prev[selectedUser] ?? []), userMsg],
      }));

      setMemories((prev) => ({
        ...prev,
        [selectedUser]: extractMemory(text, prev[selectedUser] ?? {}),
      }));

      setLoading(true);

      // TODO: Replace with real API call
      const res = await sendMessage({ user_id: selectedUser, message: text });

      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: res.assistantText,
        toolUsed: res.toolUsed,
        result: res.result,
      };

      setChats((prev) => ({
        ...prev,
        [selectedUser]: [...(prev[selectedUser] ?? []), assistantMsg],
      }));

      if (res.result) {
        setLatestResult({ toolUsed: res.toolUsed, result: res.result });
      }

      setLoading(false);
    },
    [selectedUser]
  );

  return (
    <div className="h-screen flex flex-col agent-gradient-bg">
      {/* Header */}
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
        <span className="text-xs text-muted-foreground font-mono ml-auto hidden sm:flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" />
          {selectedUser}
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
        {/* Left panel */}
        <aside
          className={`${
            leftOpen ? "w-64" : "w-0"
          } transition-all duration-200 overflow-hidden border-r bg-card/60 backdrop-blur-sm shrink-0`}
          role="complementary"
          aria-label="User and memory panel"
        >
          <div className="p-4 space-y-6 w-64">
            <UserSwitcher users={USERS} selected={selectedUser} onSelect={setSelectedUser} />
            <div className="border-t pt-4">
              <MemoryPanel memory={currentMemory} />
            </div>
          </div>
        </aside>

        {/* Center — Chat */}
        <main className="flex-1 min-w-0" role="main" aria-label="Chat conversation">
          <ChatWindow messages={currentMessages} onSend={handleSend} loading={loading} />
        </main>

        {/* Right panel */}
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
