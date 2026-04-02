import { Cloud, Sun, CloudRain, CloudSun, Users } from "lucide-react";

export function UsersCard({ data }: { data: { id: number; name: string }[] }) {
  return (
    <div className="rounded-xl border bg-card p-4 animate-card-reveal shadow-sm">
      <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5 mb-3">
        <Users className="h-3 w-3" /> Users ({data.length})
      </h4>
      <ul className="space-y-2">
        {data.map((u) => (
          <li key={u.id} className="flex items-center gap-2.5 text-sm">
            <span className="h-7 w-7 rounded-lg bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">
              {u.name[0]}
            </span>
            <span className="font-medium">{u.name}</span>
            <span className="ml-auto text-[10px] text-muted-foreground font-mono bg-secondary px-1.5 py-0.5 rounded">
              #{u.id}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

const forecastIcons: Record<string, typeof Cloud> = {
  sunny: Sun,
  rainy: CloudRain,
  cloudy: Cloud,
  "partly cloudy": CloudSun,
};

export function WeatherCard({
  data,
}: {
  data: { city: string; forecast: string; temperature_c: number };
}) {
  const Icon = forecastIcons[data.forecast] ?? Cloud;

  return (
    <div className="rounded-xl border bg-card p-4 animate-card-reveal shadow-sm">
      <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5 mb-3">
        <Cloud className="h-3 w-3" /> Weather
      </h4>
      <div className="flex items-center gap-3 mb-3">
        <div className="h-10 w-10 rounded-lg bg-accent/10 flex items-center justify-center">
          <Icon className="h-5 w-5 text-accent" />
        </div>
        <div>
          <p className="font-bold text-lg leading-none">{data.temperature_c}°C</p>
          <p className="text-xs text-muted-foreground capitalize mt-0.5">{data.forecast}</p>
        </div>
      </div>
      <div className="flex justify-between text-sm border-t pt-2">
        <span className="text-muted-foreground">City</span>
        <span className="font-semibold">{data.city}</span>
      </div>
    </div>
  );
}
