# Agent Chat + Memory

## Dummy Logic

- Messages containing **"users"** → returns a dummy users list via `get_users` tool
- Messages containing **"weather"** (+ optional city: berlin/london/tokyo/paris) → returns weather via `get_weather` tool
- Any other message → "I selected no tool for this query."
- Messages like **"my name is X"** or **"I like Y"** update the long-term memory panel

## Replacing Mock API

1. Open `src/lib/chatApi.ts`
2. Uncomment the `API_BASE` constant and set your FastAPI URL
3. Replace the `sendMessage` function body with a real `fetch` call (see the TODO comment inside)

## Backend Contract

```
POST /chat
Content-Type: application/json

Request:  { "user_id": "string", "message": "string" }
Response: { "result": <users_list | weather_object | null> }
```

Result shapes:
- Users: `[{"id":1,"name":"Alice"}, ...]`
- Weather: `{"city":"Berlin","forecast":"sunny","temperature_c":24}`

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
