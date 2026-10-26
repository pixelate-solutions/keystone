export type HealthLabel = "stable" | "strained" | "at_risk";

export type ConnectionStatus = "pending" | "syncing" | "ready" | "error";

export const APP_ROUTES = {
  dashboard: "/app",
  connect: "/app/settings",
  transactions: "/app/transactions",
  runway: "/app/runway",
  wealth: "/app/wealth",
  scenarios: "/app/scenarios",
  settings: "/app/settings",
} as const;

export const CURRENCY_CODE = "USD" as const;
