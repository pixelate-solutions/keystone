"use client";

import { useMemo } from "react";
import { usePlaidLink } from "react-plaid-link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useBillingStatus,
  useConnections,
  useCreateCheckoutSession,
  useCreatePortalSession,
  useExchangePlaidPublicToken,
  usePlaidLinkToken,
  useTriggerPlaidSync,
} from "@/lib/api/endpoints";

export default function SettingsPage() {
  const billing = useBillingStatus();
  const connections = useConnections();
  const checkout = useCreateCheckoutSession();
  const portal = useCreatePortalSession();
  const linkToken = usePlaidLinkToken();
  const exchange = useExchangePlaidPublicToken();
  const sync = useTriggerPlaidSync();

  const token = useMemo(() => linkToken.data?.link_token ?? null, [linkToken.data]);
  const plaid = usePlaidLink({
    token,
    onSuccess: async (publicToken, metadata) => {
      const response = await exchange.mutateAsync({
        public_token: publicToken,
        institution_name: metadata.institution?.name,
      });
      await sync.mutateAsync({ connection_id: response.connection_id });
      await connections.refetch();
    },
  });

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Billing and plan</CardTitle>
          <CardDescription>Free and Pro subscription management.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm">Current tier: {billing.data?.tier ?? "free"}</p>
          <p className="text-sm">Subscription status: {billing.data?.subscription_status ?? "inactive"}</p>
          <p className="text-sm">Renewal: {billing.data?.current_period_end ?? "n/a"}</p>
          <div className="flex flex-wrap gap-2">
            <Button
              onClick={async () => {
                const response = await checkout.mutateAsync();
                window.location.href = response.url;
              }}
            >
              Upgrade to Pro
            </Button>
            <Button
              variant="outline"
              onClick={async () => {
                const response = await portal.mutateAsync();
                window.location.href = response.url;
              }}
              disabled={!billing.data?.portal_available}
            >
              Manage in portal
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Data connections</CardTitle>
          <CardDescription>Manage connected institutions and trigger account sync.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button onClick={() => plaid.open()} disabled={!plaid.ready || !token}>
            Launch Plaid Link
          </Button>

          {connections.isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : connections.data?.length ? (
            connections.data.map((conn) => (
              <div key={conn.connection_id} className="rounded-md border p-3">
                <p className="text-sm font-medium">{conn.institution ?? "Institution"}</p>
                <p className="text-xs capitalize text-muted-foreground">{conn.status}</p>
                {conn.last_error ? <p className="mt-1 text-xs text-orange-700">{conn.last_error}</p> : null}
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No linked institutions.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
