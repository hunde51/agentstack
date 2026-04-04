const STORAGE_KEY = "agentstack_user_id";

/**
 * `user_id` sent to POST /chat. Override with `VITE_USER_ID`; otherwise a stable id per browser tab.
 */
export function getStableUserId(): string {
  const fromEnv = import.meta.env.VITE_USER_ID as string | undefined;
  if (fromEnv?.trim()) return fromEnv.trim();

  if (typeof window === "undefined") return "local";

  try {
    let id = sessionStorage.getItem(STORAGE_KEY);
    if (!id) {
      id = crypto.randomUUID();
      sessionStorage.setItem(STORAGE_KEY, id);
    }
    return id;
  } catch {
    return `user-${Date.now()}`;
  }
}
