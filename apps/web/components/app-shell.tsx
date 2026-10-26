"use client";

import { AIChatSidebar } from "@/components/ai-chat-sidebar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_20%_0%,#eef6f3,transparent_45%),radial-gradient(circle_at_95%_15%,#f6f3ea,transparent_35%),#f8faf9]">
      <AIChatSidebar />
      <main className="mx-auto max-w-7xl px-6 py-6">{children}</main>
    </div>
  );
}
