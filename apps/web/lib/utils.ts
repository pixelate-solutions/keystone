import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatUSD(cents: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(cents / 100);
}

export function healthTone(status: "stable" | "strained" | "at_risk") {
  if (status === "stable") return "bg-emerald-50 text-emerald-700 border-emerald-200";
  if (status === "strained") return "bg-amber-50 text-amber-700 border-amber-200";
  return "bg-orange-50 text-orange-700 border-orange-200";
}
