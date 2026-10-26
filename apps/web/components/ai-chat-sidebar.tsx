"use client";

import { Bot, PanelRightClose, PanelRightOpen, SendHorizonal } from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const starterQuestions = [
  "What changed in spend categories this week?",
  "How does payroll affect runway over 90 days?",
  "What near-term moves improve long-term wealth trajectory?",
];

export function AIChatSidebar() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; text: string }>>([
    {
      role: "assistant",
      text: "I can help interpret transactions, runway shifts, and long-term planning tradeoffs.",
    },
  ]);
  const [draft, setDraft] = useState("");

  const quickReplies = useMemo(() => starterQuestions, []);

  const send = (text: string) => {
    const value = text.trim();
    if (!value) return;

    setMessages((current) => [
      ...current,
      { role: "user", text: value },
      {
        role: "assistant",
        text: "Use the command center cards to validate this with current categories, runway drivers, and obligations timing.",
      },
    ]);
    setDraft("");
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen((current) => !current)}
        className="fixed right-4 top-24 z-40 inline-flex items-center gap-2 rounded-md border border-border bg-white px-3 py-2 text-xs font-medium text-slate-700 shadow-sm"
      >
        {open ? <PanelRightClose className="h-4 w-4" /> : <PanelRightOpen className="h-4 w-4" />}
        AI Guide
      </button>

      <aside
        className={`fixed right-0 top-16 z-30 h-[calc(100vh-4rem)] w-[340px] border-l border-border bg-white/95 backdrop-blur transition-transform duration-300 ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex h-full flex-col">
          <div className="border-b border-border px-4 py-3">
            <p className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <Bot className="h-4 w-4 text-emerald-700" />
              Keystone AI Guide
            </p>
            <p className="mt-1 text-xs text-slate-600">Understand what changed and what to do next.</p>
          </div>

          <div className="flex-1 space-y-2 overflow-y-auto px-4 py-3">
            {messages.map((msg, idx) => (
              <div
                key={`${msg.role}-${idx}`}
                className={`rounded-md p-2 text-xs ${
                  msg.role === "assistant" ? "bg-emerald-50 text-emerald-900" : "bg-slate-100 text-slate-900"
                }`}
              >
                {msg.text}
              </div>
            ))}

            <div className="space-y-2 pt-1">
              {quickReplies.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => send(q)}
                  className="w-full rounded-md border border-border px-2 py-1.5 text-left text-xs text-slate-700 hover:bg-muted"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          <form
            className="border-t border-border p-3"
            onSubmit={(e) => {
              e.preventDefault();
              send(draft);
            }}
          >
            <div className="flex gap-2">
              <Input
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="Ask about runway, spend, or planning..."
              />
              <Button type="submit" size="sm">
                <SendHorizonal className="h-4 w-4" />
              </Button>
            </div>
          </form>
        </div>
      </aside>
    </>
  );
}
