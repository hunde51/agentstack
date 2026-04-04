export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  toolUsed?: string | null;
  result?: any;
}

export interface UserMemory {
  name?: string;
  likes?: string[];
}
