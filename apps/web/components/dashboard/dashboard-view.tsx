"use client";

import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useAnomalies,
  useCashPosition,
  useGuidanceSummary,
  useHealthSignals,
  useObligations,
  usePayrollSummary,
  useRunway,
  useTransactions,
} from "@/lib/api/endpoints";
import { formatUSD, healthTone } from "@/lib/utils";

function SummaryStrip() {
  const cash = useCashPosition();
  const runway30 = useRunway(30);
  const runway180 = useRunway(180);
  const health = useHealthSignals();

  if (cash.isLoading || runway30.isLoading || runway180.isLoading || health.isLoading) {
    return <Skeleton className="h-24 w-full" />;
  }

  if (!cash.data || !runway30.data || !runway180.data || !health.data) {
    return (
      <Card>
        <CardContent className="p-5 text-sm text-muted-foreground">
          Data unavailable. Verify API auth and demo seed state.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-3 md:grid-cols-4">
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Cash position</CardDescription>
          <CardTitle>{formatUSD(cash.data.amount_cents)}</CardTitle>
        </CardHeader>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Short-term runway</CardDescription>
          <CardTitle>{runway30.data.runway_days} days</CardTitle>
        </CardHeader>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Long-horizon runway</CardDescription>
          <CardTitle>{runway180.data.runway_days} days</CardTitle>
        </CardHeader>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Health</CardDescription>
          <CardTitle>
            <Badge className={healthTone(health.data.status)}>{health.data.status.replace("_", " ")}</Badge>
          </CardTitle>
        </CardHeader>
      </Card>
    </div>
  );
}

export function DashboardView() {
  const runway = useRunway(90);
  const obligations = useObligations();
  const health = useHealthSignals();
  const anomalies = useAnomalies(8);
  const guidance = useGuidanceSummary();
  const transactions = useTransactions(24);
  const payroll = usePayrollSummary();

  return (
    <div className="space-y-4">
      <SummaryStrip />

      <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Short-term runway control</CardTitle>
              <CardDescription>90-day posture with explainable drivers and obligation pressure.</CardDescription>
            </CardHeader>
            <CardContent>
              {runway.isLoading ? (
                <Skeleton className="h-28 w-full" />
              ) : runway.data ? (
                <div className="space-y-3">
                  <p className="text-2xl font-semibold">{runway.data.runway_days} days</p>
                  <p className="text-sm text-muted-foreground">
                    Projected end cash: {formatUSD(runway.data.projected_end_cash_cents)}
                  </p>
                  <details className="rounded-md border p-3 text-sm">
                    <summary className="cursor-pointer font-medium">Why this changed</summary>
                    <ul className="mt-2 space-y-2 text-muted-foreground">
                      {runway.data.drivers.map((driver) => (
                        <li key={driver.label}>
                          <span className="font-medium text-foreground">{driver.label}:</span> {driver.detail}
                        </li>
                      ))}
                    </ul>
                  </details>
                  <Link href="/app/runway">
                    <Button variant="outline" size="sm">Deep dive runway</Button>
                  </Link>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No runway data yet.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Categorized transactions</CardTitle>
              <CardDescription>Largest categories and recent activity to understand current cashflow drivers.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {transactions.isLoading ? (
                <Skeleton className="h-24 w-full" />
              ) : transactions.data ? (
                <>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {transactions.data.categories.slice(0, 4).map((category) => (
                      <div key={category.category} className="rounded-md border p-3">
                        <p className="text-xs uppercase tracking-wide text-muted-foreground">{category.category}</p>
                        <p className="mt-1 text-sm font-medium">{formatUSD(category.total_cents)}</p>
                        <p className="text-xs text-muted-foreground">{category.transaction_count} transactions</p>
                      </div>
                    ))}
                  </div>

                  <div className="space-y-2 rounded-md border p-3">
                    {transactions.data.items.slice(0, 5).map((txn) => (
                      <div key={txn.txn_id} className="flex items-center justify-between text-sm">
                        <div>
                          <p className="font-medium">{txn.name}</p>
                          <p className="text-xs text-muted-foreground">{txn.category ?? "uncategorized"}</p>
                        </div>
                        <p>{formatUSD(txn.amount_cents)}</p>
                      </div>
                    ))}
                  </div>

                  <Link href="/app/transactions">
                    <Button variant="outline" size="sm">Deep dive transactions</Button>
                  </Link>
                </>
              ) : (
                <p className="text-sm text-muted-foreground">No transaction data yet.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Upcoming obligations</CardTitle>
              <CardDescription>Payroll, vendor, and debt timing over the next cycle.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {obligations.isLoading ? (
                <Skeleton className="h-24 w-full" />
              ) : obligations.data?.items.length ? (
                obligations.data.items.map((item) => (
                  <div key={item.obligation_id} className="flex items-center justify-between rounded-md border p-3">
                    <div>
                      <p className="text-sm font-medium">{item.name}</p>
                      <p className="text-xs text-muted-foreground">Due {item.due_date}</p>
                    </div>
                    <div className="text-sm font-medium">{formatUSD(item.amount_cents)}</div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No obligations in the current window.</p>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Monitoring feed</CardTitle>
              <CardDescription>Latest anomalies and confidence signals.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {anomalies.isLoading ? (
                <Skeleton className="h-24 w-full" />
              ) : anomalies.data?.length ? (
                anomalies.data.map((item) => (
                  <div key={item.anomaly_id} className="rounded-md border p-3">
                    <p className="text-sm font-medium">{item.title}</p>
                    <p className="text-xs text-muted-foreground">{item.explanation}</p>
                    <p className="mt-1 text-xs text-muted-foreground">Confidence: {item.confidence}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No anomalies detected in this period.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Long-term wealth planning</CardTitle>
              <CardDescription>Balance growth, payroll, and operating buffer for durable outcomes.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {payroll.isLoading ? (
                <Skeleton className="h-16 w-full" />
              ) : payroll.data ? (
                <>
                  <p>Baseline payroll: {formatUSD(payroll.data.baseline_monthly_cents)}</p>
                  <p>Planned hires load: {formatUSD(payroll.data.planned_hires_monthly_cents)}</p>
                  <p>Payroll / estimated revenue: {payroll.data.payroll_pct_of_revenue}%</p>
                  <p>Suggested hiring horizon: {payroll.data.can_hire_until ?? "n/a"}</p>
                  <Link href="/app/wealth">
                    <Button variant="outline" size="sm">Deep dive wealth plan</Button>
                  </Link>
                </>
              ) : (
                <p className="text-muted-foreground">No payroll planning profile yet.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>What changed since last week</CardTitle>
            </CardHeader>
            <CardContent>
              {guidance.isLoading ? (
                <Skeleton className="h-16 w-full" />
              ) : (
                <>
                  <p className="text-sm text-muted-foreground">{guidance.data?.summary}</p>
                  <ul className="mt-3 space-y-1 text-xs text-muted-foreground">
                    {guidance.data?.key_drivers.map((driver) => <li key={driver}>• {driver}</li>)}
                  </ul>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Health signals</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {health.isLoading ? (
                <Skeleton className="h-14 w-full" />
              ) : health.data ? (
                health.data.signals.map((signal) => (
                  <div key={signal.summary} className="rounded-md border p-3">
                    <p className="text-sm font-medium">{signal.summary}</p>
                    <p className="text-xs text-muted-foreground">{signal.reason}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No health signals yet.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
