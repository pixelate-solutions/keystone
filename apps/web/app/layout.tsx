import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";

import { Providers } from "@/components/providers";
import { GlobalNavbar } from "@/components/site/global-navbar";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: "Keystone",
  description: "AI-powered financial command center for operators.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const publishableKey =
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || "pk_test_Y2xlcmtfdGVzdF9wbGFjZWhvbGRlcg";

  return (
    <ClerkProvider publishableKey={publishableKey}>
      <html lang="en">
        <body>
          <Providers>
            <GlobalNavbar />
            {children}
          </Providers>
        </body>
      </html>
    </ClerkProvider>
  );
}
