"use client";

import { APP_ROUTES } from "@keystone/shared";
import { OrganizationSwitcher, SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";
import { Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const marketingNav = [
  { href: "/#features", label: "Features" },
  { href: "/#how-it-works", label: "How it works" },
  { href: "/#insights", label: "Outcomes" },
  { href: "/#pricing", label: "Pricing" },
  { href: "/#contact", label: "Contact" },
];

const appNav = [
  { href: APP_ROUTES.dashboard, label: "Command Center" },
  { href: APP_ROUTES.transactions, label: "Transactions" },
  { href: APP_ROUTES.runway, label: "Runway" },
  { href: APP_ROUTES.wealth, label: "Wealth Plan" },
  { href: APP_ROUTES.scenarios, label: "Scenarios" },
  { href: APP_ROUTES.settings, label: "Settings" },
];

export function GlobalNavbar() {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const isAppRoute = pathname.startsWith("/app");

  const navItems = useMemo(() => (isAppRoute ? appNav : marketingNav), [isAppRoute]);

  return (
    <header className="sticky top-0 z-50 border-b border-border/70 bg-background/85 backdrop-blur-xl">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-6">
        <Link href="/" className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-900">
          keystone
        </Link>

        <nav className="hidden items-center gap-6 md:flex">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "text-sm text-slate-600 transition-colors hover:text-slate-900",
                pathname === item.href && "text-slate-900"
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <SignedOut>
            <SignInButton mode="modal" forceRedirectUrl="/app/settings" fallbackRedirectUrl="/app/settings">
              <Button size="sm">Start free</Button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <OrganizationSwitcher hidePersonal appearance={{ elements: { rootBox: "hidden lg:block" } }} />
            <UserButton afterSignOutUrl="/" />
          </SignedIn>
        </div>

        <button
          type="button"
          className="inline-flex items-center justify-center rounded-md border border-border bg-white p-2 text-slate-700 md:hidden"
          aria-label="Toggle navigation"
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </button>
      </div>

      {menuOpen && (
        <div className="border-t border-border/70 bg-white md:hidden">
          <div className="mx-auto flex max-w-7xl flex-col gap-2 px-6 py-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-md px-3 py-2 text-sm text-slate-700 hover:bg-muted"
                onClick={() => setMenuOpen(false)}
              >
                {item.label}
              </Link>
            ))}

            <div className="mt-2 border-t border-border/70 pt-3">
              <SignedOut>
                <SignInButton mode="modal" forceRedirectUrl="/app/settings" fallbackRedirectUrl="/app/settings">
                  <Button className="w-full">Start free</Button>
                </SignInButton>
              </SignedOut>
              <SignedIn>
                <div className="flex items-center justify-end gap-2">
                  <UserButton afterSignOutUrl="/" />
                </div>
              </SignedIn>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
