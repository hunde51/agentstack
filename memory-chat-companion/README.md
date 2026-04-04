# Agent Chat + Memory

## Frontend ↔ backend

- `src/lib/chatApi.ts` calls `POST /chat` with `{ user_id, message }`.
- **Dev:** Vite proxies `/api/*` → `http://127.0.0.1:8000` (see `vite.config.ts`). The app uses `/api` as the base in development unless `VITE_API_BASE` is set.
- **Prod / custom URL:** set `VITE_API_BASE` to your FastAPI origin (no trailing slash).
- **`user_id`:** set `VITE_USER_ID` for a fixed id, or omit it to use a stable id per browser tab (`sessionStorage`).

## Backend contract (current)

```
POST /chat
Content-Type: application/json

Request:  { "user_id": "string", "message": "string" }
Response: {
  "result": "string",
  "tool_used": "get_users" | "get_weather" | null,
  "tool_result": <structured tool output> | null
}
```

The left **Memory** panel still uses client-side extraction from messages (`memoryExtractor.ts`). The backend also merges similar rules into Redis for the agent; a `GET /memory` API is not implemented yet.

## Style Guide

### Color Tokens (HSL via CSS variables)
| Token | Value | Usage |
|---|---|---|
| `--primary` | 235 65% 55% | Buttons, user bubbles, active states |
| `--accent` | 170 60% 42% | Likes chips, weather accents, success |
| `--background` | 220 20% 97% | Page background |
| `--card` | 0 0% 100% | Cards, panels, assistant bubbles |
| `--muted` | 220 15% 94% | Disabled states, secondary surfaces |
| `--foreground` | 220 25% 10% | Primary text |
| `--muted-foreground` | 220 10% 50% | Labels, placeholders |

### Type Scale
- **Display/Headings**: Plus Jakarta Sans 700 (bold)
- **Body**: Plus Jakarta Sans 400–500
- **Code/Mono**: JetBrains Mono 400–500
- **Sizes**: 10px (labels) · 12px (caption) · 14px (body/sm) · 18px (lg) · 24px (display)

### Spacing System
- Base unit: 4px (Tailwind default)
- Common: `gap-1.5` (6px), `p-3` (12px), `p-4` (16px), `gap-2.5` (10px)
- Panel widths: Left 256px, Right 320px

### Interaction & Motion
- `msg-in`: slide-up + fade (300ms ease-out, 60ms stagger)
- `card-reveal`: scale-up + fade (400ms ease-out)
- `fade-in`: opacity transition (300ms)
- Buttons: `active:scale-95` press feedback
- Focus: `ring-2 ring-ring` on interactive elements
- Disabled: `opacity-50` + `cursor-not-allowed`
