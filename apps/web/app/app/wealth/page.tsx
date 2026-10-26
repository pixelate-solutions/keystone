"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useGuidanceQuestions, usePayrollSummary, useRunway } from "@/lib/api/endpoints";
import { formatUSD } from "@/lib/utils";

export default function WealthPage() {
  const payroll = usePayrollSummary();
  const runway = useRunway(180);
  const guidanceQuestions = useGuidanceQuestions();

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Long-term wealth planning</CardTitle>
          <CardDescription>Connect growth decisions to runway durability and payroll loading.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>180d runway: {runway.data?.runway_days ?? "-"} days</p>
          <p>Projected end cash: {formatUSD(runway.data?.projected_end_cash_cents ?? 0)}</p>
          <p>Baseline payroll: {formatUSD(payroll.data?.baseline_monthly_cents ?? 0)}</p>
          <p>Planned hires load: {formatUSD(payroll.data?.planned_hires_monthly_cents ?? 0)}</p>
          <p>Payroll % of estimated revenue: {payroll.data?.payroll_pct_of_revenue ?? 0}%</p>
          <p>Hiring horizon: {payroll.data?.can_hire_until ?? "n/a"}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Strategic prompts</CardTitle>
          <CardDescription>Questions to guide long-term planning with current operating constraints.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {guidanceQuestions.data?.questions?.length ? (
            guidanceQuestions.data.questions.map((question) => (
              <div key={question} className="rounded-md border p-3">
                {question}
              </div>
            ))
          ) : (
            <p className="text-muted-foreground">No prompts available yet.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
