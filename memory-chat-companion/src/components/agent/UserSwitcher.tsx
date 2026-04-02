import type { DummyUser } from "@/lib/types";
import { User } from "lucide-react";

interface Props {
  users: DummyUser[];
  selected: string;
  onSelect: (id: string) => void;
}

export default function UserSwitcher({ users, selected, onSelect }: Props) {
  return (
    <nav className="space-y-1" aria-label="User selector">
      <h3 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2.5 px-1">
        Users
      </h3>
      {users.map((u) => (
        <button
          key={u.id}
          onClick={() => onSelect(u.id)}
          aria-pressed={selected === u.id}
          className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
            selected === u.id
              ? "bg-primary text-primary-foreground shadow-sm"
              : "hover:bg-secondary text-foreground active:scale-[0.98]"
          }`}
        >
          <div
            className={`h-6 w-6 rounded-md flex items-center justify-center text-xs ${
              selected === u.id
                ? "bg-primary-foreground/20"
                : "bg-secondary"
            }`}
          >
            <User className="h-3.5 w-3.5" />
          </div>
          <span className="truncate font-mono text-xs">{u.label}</span>
        </button>
      ))}
    </nav>
  );
}
