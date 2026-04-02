import type { UserMemory } from "@/lib/types";
import { Brain, Sparkles } from "lucide-react";

interface Props {
  memory: UserMemory;
}

export default function MemoryPanel({ memory }: Props) {
  const hasMemory = memory.name || (memory.likes && memory.likes.length > 0);

  return (
    <div className="space-y-3">
      <h3 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5 px-1">
        <Brain className="h-3 w-3" />
        Long-term Memory
      </h3>
      {!hasMemory ? (
        <div className="flex flex-col items-center gap-2 py-6 text-center">
          <div className="h-8 w-8 rounded-lg bg-secondary flex items-center justify-center">
            <Sparkles className="h-4 w-4 text-muted-foreground" />
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            No memory yet.<br />
            Try saying <span className="font-mono text-foreground">"my name is…"</span>
          </p>
        </div>
      ) : (
        <div className="space-y-3 animate-fade-in rounded-lg border bg-card p-3">
          {memory.name && (
            <div className="text-sm">
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">Name</span>
              <p className="font-semibold mt-0.5">{memory.name}</p>
            </div>
          )}
          {memory.likes && memory.likes.length > 0 && (
            <div>
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">Likes</span>
              <div className="flex flex-wrap gap-1.5 mt-1.5">
                {memory.likes.map((l) => (
                  <span
                    key={l}
                    className="inline-block px-2.5 py-0.5 rounded-full text-xs font-medium bg-accent/15 text-accent border border-accent/20"
                  >
                    {l}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
