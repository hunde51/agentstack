export interface SendMessageRequest {
  user_id: string;
  message: string;
}

export interface SendMessageResponse {
  /** Structured tool payload when the API provides it; otherwise null. */
  result: unknown;
  assistantText: string;
  toolUsed: string | null;
}

function apiBase(): string {
  const fromEnv = import.meta.env.VITE_API_BASE as string | undefined;
  if (fromEnv?.trim()) return fromEnv.replace(/\/$/, "");
  if (import.meta.env.DEV) return "/api";
  return "http://127.0.0.1:8000";
}

/**
 * POST /chat — backend expects `{ user_id, message }` and returns
 * `{ result, tool_used?, tool_result? }`.
 */
export async function sendMessage(req: SendMessageRequest): Promise<SendMessageResponse> {
  const res = await fetch(`${apiBase()}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: req.user_id, message: req.message }),
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const err = await res.json();
      if (typeof err?.detail === "string") detail = err.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail || `HTTP ${res.status}`);
  }

  const data = (await res.json()) as {
    result?: unknown;
    tool_used?: string | null;
    tool_result?: unknown;
  };

  const raw = data.result;
  const assistantText =
    typeof raw === "string"
      ? raw
      : raw != null
        ? JSON.stringify(raw)
        : "";

  return {
    assistantText: assistantText.trim() ? assistantText : "(Empty response)",
    toolUsed: data.tool_used ?? null,
    result: data.tool_result ?? null,
  };
}
