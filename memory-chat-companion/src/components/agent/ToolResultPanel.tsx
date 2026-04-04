import { useState } from "react";
import { Code2, LayoutList, Braces } from "lucide-react";
import { UsersCard, WeatherCard } from "./ResultCards";

interface Props {
  toolUsed: string | null;
  result: any;
}

type Tab = "formatted" | "json";

export default function ToolResultPanel({ toolUsed, result }: Props) {
  const [tab, setTab] = useState<Tab>("formatted");

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-muted-foreground text-sm gap-3 p-6">
        <div className="h-12 w-12 rounded-xl bg-secondary flex items-center justify-center">
          <Code2 className="h-6 w-6 opacity-40" />
        </div>
        <p className="font-medium">No tool result yet</p>
        <p className="text-xs text-center leading-relaxed max-w-[200px]">
          When the API returns structured tool output, it will show here. The chat uses the agent reply in
          the center panel.
        </p>
      </div>
    );
  }

  const hasFormattedView =
    (toolUsed === "get_users" && Array.isArray(result)) ||
    (toolUsed === "get_weather" && result?.city);

  return (
    <div className="flex flex-col h-full">
      {/* Header with tabs */}
      <div className="p-4 pb-0 space-y-3">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Tool Result
          {toolUsed && (
            <span className="ml-2 font-mono text-primary normal-case">
              {toolUsed}
            </span>
          )}
        </h3>
        <div className="flex gap-1 p-0.5 rounded-lg bg-secondary" role="tablist">
          <button
            role="tab"
            aria-selected={tab === "formatted"}
            onClick={() => setTab("formatted")}
            className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              tab === "formatted"
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <LayoutList className="h-3 w-3" />
            Formatted
          </button>
          <button
            role="tab"
            aria-selected={tab === "json"}
            onClick={() => setTab("json")}
            className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              tab === "json"
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <Braces className="h-3 w-3" />
            JSON
          </button>
        </div>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-y-auto p-4">
        {tab === "formatted" ? (
          <div className="animate-fade-in">
            {hasFormattedView ? (
              <>
                {toolUsed === "get_users" && Array.isArray(result) && (
                  <UsersCard data={result} />
                )}
                {toolUsed === "get_weather" && result?.city && (
                  <WeatherCard data={result} />
                )}
              </>
            ) : (
              <p className="text-sm text-muted-foreground italic">
                No formatted view available for this result.
              </p>
            )}
          </div>
        ) : (
          <div className="animate-fade-in">
            <pre className="rounded-lg bg-secondary p-3 text-xs font-mono overflow-x-auto text-secondary-foreground whitespace-pre-wrap leading-relaxed">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
