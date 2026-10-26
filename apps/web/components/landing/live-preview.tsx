"use client";

import { ArrowUpRight, BellRing, CircleDollarSign, Timer } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatUSD } from "@/lib/utils";

type Snapshot = {
  cashCents: number;
  runwayDays: number;
  obligationsCents: number;
  anomalies: number;
  tone: "Stable" | "Strained" | "At-risk";
};

const snapshots: Snapshot[] = [
  {
    cashCents: 10700000,
    runwayDays: 218,
    obligationsCents: 412000,
    anomalies: 1,
    tone: "Stable",
  },
  {
    cashCents: 9340000,
    runwayDays: 176,
    obligationsCents: 648000,
    anomalies: 2,
    tone: "Strained",
  },
  {
    cashCents: 8450000,
    runwayDays: 149,
    obligationsCents: 713000,
    anomalies: 3,
    tone: "Strained",
  },
];

export function LivePreview() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const id = window.setInterval(() => {
      setIndex((current) => (current + 1) % snapshots.length);
    }, 2600);

    return () => window.clearInterval(id);
  }, []);

  const snapshot = snapshots[index];
  const obligationsPercent = useMemo(
    () => Math.min(100, Math.round((snapshot.obligationsCents / Math.max(snapshot.cashCents, 1)) * 1000)),
    [snapshot]
  );

  return (
    <Card className="relative overflow-hidden border-emerald-100/80 bg-white/90 shadow-[0_20px_80px_-45px_rgba(17,94,89,0.65)]">
      <div className="pointer-events-none absolute -right-24 -top-24 h-44 w-44 rounded-full bg-emerald-100/70 blur-3xl" />
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <span className="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
          Command center live state
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <Metric icon={CircleDollarSign} label="Cash position" value={formatUSD(snapshot.cashCents)} />
          <Metric icon={Timer} label="Runway" value={`${snapshot.runwayDays} days`} />
        </div>

        <div className="rounded-lg border border-border/70 bg-muted/40 p-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Upcoming obligations load</span>
            <span className="font-medium">{formatUSD(snapshot.obligationsCents)}</span>
          </div>
          <div className="mt-2 h-2 rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all duration-700"
              style={{ width: `${obligationsPercent}%` }}
            />
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-lg border border-border/70 bg-white p-3 text-sm">
            <p className="text-muted-foreground">Health signal</p>
            <p className="mt-1 font-semibold">{snapshot.tone}</p>
          </div>
          <div className="rounded-lg border border-border/70 bg-white p-3 text-sm">
            <p className="flex items-center gap-1 text-muted-foreground">
              <BellRing className="h-3.5 w-3.5" /> Recent anomalies
            </p>
            <p className="mt-1 font-semibold">{snapshot.anomalies} in last 7 days</p>
          </div>
        </div>

        <div className="rounded-lg border border-emerald-100 bg-emerald-50 p-3 text-sm text-emerald-900">
          <p className="font-medium">Why this changed</p>
          <p className="mt-1 text-emerald-800/90">
            Vendor payments concentrated this week and infrastructure spend is trending up.
            <span className="ml-1 inline-flex items-center gap-1 font-medium">
              Review timing controls <ArrowUpRight className="h-3.5 w-3.5" />
            </span>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof CircleDollarSign;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-border/70 bg-white p-3">
      <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Icon className="h-3.5 w-3.5" />
        {label}
      </p>
      <p className="mt-1 text-lg font-semibold tracking-tight">{value}</p>
    </div>
  );
}
