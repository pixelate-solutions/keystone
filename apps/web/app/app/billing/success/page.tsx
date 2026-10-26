import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function BillingSuccessPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Subscription confirmed</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <p>Pro features are now available for this organization.</p>
        <Link href="/app/settings">
          <Button>Return to settings</Button>
        </Link>
      </CardContent>
    </Card>
  );
}
