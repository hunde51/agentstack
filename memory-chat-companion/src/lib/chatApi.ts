// API adapter layer — swap mock with real POST /chat later.

import type { ChatMessage } from "@/lib/types";

// TODO: Replace with real API base URL
// const API_BASE = "http://localhost:8000";

const DUMMY_USERS = [
  { id: 1, name: "Alice" },
  { id: 2, name: "Bob" },
  { id: 3, name: "Charlie" },
];

const DUMMY_WEATHER: Record<string, { city: string; forecast: string; temperature_c: number }> = {
  berlin: { city: "Berlin", forecast: "sunny", temperature_c: 24 },
  london: { city: "London", forecast: "rainy", temperature_c: 14 },
  tokyo: { city: "Tokyo", forecast: "cloudy", temperature_c: 19 },
  paris: { city: "Paris", forecast: "partly cloudy", temperature_c: 21 },
};

export interface SendMessageRequest {
  user_id: string;
  message: string;
}

export interface SendMessageResponse {
  result: any;
  assistantText: string;
  toolUsed: string | null;
}

/**
 * Mock implementation of POST /chat
 * TODO: Replace body with:
 *   const res = await fetch(`${API_BASE}/chat`, {
 *     method: "POST",
 *     headers: { "Content-Type": "application/json" },
 *     body: JSON.stringify({ user_id, message }),
 *   });
 *   return res.json();
 */
export async function sendMessage(req: SendMessageRequest): Promise<SendMessageResponse> {
  // Simulate network latency
  await new Promise((r) => setTimeout(r, 600));

  const msg = req.message.toLowerCase();

  if (msg.includes("users")) {
    return {
      result: DUMMY_USERS,
      assistantText: "I used the **get_users** tool. Here are the results:",
      toolUsed: "get_users",
    };
  }

  if (msg.includes("weather")) {
    const cityMatch = Object.keys(DUMMY_WEATHER).find((c) => msg.includes(c));
    const weather = DUMMY_WEATHER[cityMatch ?? "berlin"];
    return {
      result: weather,
      assistantText: `I used the **get_weather** tool for ${weather.city}:`,
      toolUsed: "get_weather",
    };
  }

  return {
    result: null,
    assistantText: "I selected no tool for this query. Try asking about **users** or **weather**.",
    toolUsed: null,
  };
}
