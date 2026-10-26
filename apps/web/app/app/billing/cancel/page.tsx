import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function BillingCancelPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Checkout canceled</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <p>No billing changes were made. You can upgrade whenever you are ready.</p>
        <Link href="/app/settings">
          <Button variant="outline">Back to settings</Button>
        </Link>
      </CardContent>
    </Card>
  );
}
