"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useTransactions } from "@/lib/api/endpoints";
import { formatUSD } from "@/lib/utils";

export default function TransactionsPage() {
  const transactions = useTransactions(120);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Categorized transactions</CardTitle>
          <CardDescription>Study cashflow composition by category and merchant activity.</CardDescription>
        </CardHeader>
        <CardContent>
          {transactions.isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : transactions.data ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {transactions.data.categories.map((category) => (
                <div key={category.category} className="rounded-md border p-3">
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">{category.category}</p>
                  <p className="mt-1 text-base font-semibold">{formatUSD(category.total_cents)}</p>
                  <p className="text-xs text-muted-foreground">{category.transaction_count} txns</p>
                </div>
              ))}
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent ledger</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {transactions.isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : transactions.data?.items.length ? (
            transactions.data.items.map((txn) => (
              <div key={txn.txn_id} className="flex items-center justify-between rounded-md border p-3 text-sm">
                <div>
                  <p className="font-medium">{txn.name}</p>
                  <p className="text-xs text-muted-foreground">{txn.category ?? "uncategorized"}</p>
                </div>
                <div className="text-right">
                  <p className="font-medium">{formatUSD(txn.amount_cents)}</p>
                  <p className="text-xs text-muted-foreground">{txn.date}</p>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No transactions available.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
