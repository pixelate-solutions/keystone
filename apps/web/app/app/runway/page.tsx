"use client";

import { useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useRunway } from "@/lib/api/endpoints";
import { formatUSD } from "@/lib/utils";

export default function RunwayPage() {
  const [days, setDays] = useState(30);
  const runway = useRunway(days);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Runway deep dive</CardTitle>
        <CardDescription>Compare short and long horizons with explainable forecast drivers.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Tabs value={String(days)} onValueChange={(v) => setDays(Number(v))}>
          <TabsList>
            <TabsTrigger value="30">30d</TabsTrigger>
            <TabsTrigger value="60">60d</TabsTrigger>
            <TabsTrigger value="90">90d</TabsTrigger>
            <TabsTrigger value="180">180d</TabsTrigger>
          </TabsList>
          <TabsContent value={String(days)}>
            {runway.data ? (
              <div className="space-y-3">
                <p className="text-2xl font-semibold">{runway.data.runway_days} days</p>
                <p className="text-sm text-muted-foreground">
                  Projected end cash: {formatUSD(runway.data.projected_end_cash_cents)}
                </p>
                <div className="space-y-2">
                  {runway.data.drivers.map((driver) => (
                    <div key={driver.label} className="rounded-md border p-3 text-sm">
                      <p className="font-medium">{driver.label}</p>
                      <p className="text-muted-foreground">{driver.detail}</p>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Runway data unavailable.</p>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
