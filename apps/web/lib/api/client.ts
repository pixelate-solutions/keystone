import { z } from "zod";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Method = "GET" | "POST";

export async function apiRequest<T>(
  path: string,
  schema: z.ZodType<T>,
  opts?: {
    method?: Method;
    body?: unknown;
    token?: string | null;
  }
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: opts?.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      ...(opts?.token ? { Authorization: `Bearer ${opts.token}` } : {}),
    },
    body: opts?.body ? JSON.stringify(opts.body) : undefined,
    cache: "no-store",
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed: ${response.status}`);
  }

  const json = await response.json();
  return schema.parse(json);
}
