"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCreateScenario, useRunway, useScenarios } from "@/lib/api/endpoints";

export default function ScenariosPage() {
  const [name, setName] = useState("Conservative");
  const [revenueDelta, setRevenueDelta] = useState(-10);
  const [termsShift, setTermsShift] = useState(10);

  const scenarios = useScenarios();
  const create = useCreateScenario();
  const runway = useRunway(90, scenarios.data?.[0]?.scenario_id);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await create.mutateAsync({
      name,
      revenue_delta_pct: revenueDelta,
      vendor_terms_shift_days: termsShift,
    });
    await scenarios.refetch();
    await runway.refetch();
  };

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Scenario builder</CardTitle>
          <CardDescription>Model runway impact from timing and revenue shifts.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-3" onSubmit={submit}>
            <div className="space-y-1">
              <Label>Name</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Revenue delta (%)</Label>
              <Input
                type="number"
                value={revenueDelta}
                onChange={(e) => setRevenueDelta(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label>Vendor terms shift (days)</Label>
              <Input
                type="number"
                value={termsShift}
                onChange={(e) => setTermsShift(Number(e.target.value))}
              />
            </div>
            <Button type="submit" disabled={create.isPending}>
              Save scenario
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Scenario list</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {scenarios.data?.map((scenario) => (
            <div key={scenario.scenario_id} className="rounded-md border p-3">
              <p className="text-sm font-medium">{scenario.name}</p>
              <p className="text-xs text-muted-foreground">
                Revenue {scenario.revenue_delta_pct}% · Terms +{scenario.vendor_terms_shift_days}d
              </p>
            </div>
          ))}
          <div className="rounded-md border p-3 text-sm">
            Modeled runway under selected scenario: {runway.data?.runway_days ?? "-"} days
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
