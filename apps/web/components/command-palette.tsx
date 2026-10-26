"use client";

import { APP_ROUTES } from "@keystone/shared";
import { Command } from "cmdk";
import { Command as CommandIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";

const items = [
  { label: "Dashboard", value: APP_ROUTES.dashboard },
  { label: "Transactions", value: APP_ROUTES.transactions },
  { label: "Runway", value: APP_ROUTES.runway },
  { label: "Wealth plan", value: APP_ROUTES.wealth },
  { label: "Scenarios", value: APP_ROUTES.scenarios },
  { label: "Settings", value: APP_ROUTES.settings },
];

export function CommandPalette() {
  const router = useRouter();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((current) => !current);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 rounded-md border px-3 py-1.5 text-sm text-muted-foreground hover:bg-muted"
      >
        <CommandIcon className="h-3 w-3" />
        Command menu
      </button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="p-0">
          <DialogTitle className="sr-only">Command menu</DialogTitle>
          <Command className="rounded-lg border">
            <Command.Input className="w-full border-b px-4 py-3 text-sm outline-none" placeholder="Jump to..." />
            <Command.List className="max-h-80 overflow-y-auto p-2">
              <Command.Empty className="px-3 py-4 text-sm text-muted-foreground">No results</Command.Empty>
              <Command.Group heading="Navigation" className="text-xs text-muted-foreground">
                {items.map((item) => (
                  <Command.Item
                    key={item.value}
                    value={item.value}
                    onSelect={() => {
                      router.push(item.value);
                      setOpen(false);
                    }}
                    className="cursor-pointer rounded px-3 py-2 text-sm hover:bg-muted"
                  >
                    {item.label}
                  </Command.Item>
                ))}
              </Command.Group>
            </Command.List>
          </Command>
        </DialogContent>
      </Dialog>
    </>
  );
}
