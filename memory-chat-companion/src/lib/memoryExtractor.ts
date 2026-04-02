import type { UserMemory } from "@/lib/types";

/**
 * Extract simple facts from a user message and merge into existing memory.
 * Rules:
 *  - "my name is X" -> sets name
 *  - "I like Y"     -> adds Y to likes (deduped)
 */
export function extractMemory(message: string, existing: UserMemory): UserMemory {
  const mem = { ...existing, likes: [...(existing.likes ?? [])] };

  const nameMatch = message.match(/my name is (\w+)/i);
  if (nameMatch) {
    mem.name = nameMatch[1];
  }

  const likeMatch = message.match(/i like (\w+)/i);
  if (likeMatch) {
    const item = likeMatch[1].toLowerCase();
    if (!mem.likes.includes(item)) {
      mem.likes.push(item);
    }
  }

  return mem;
}
