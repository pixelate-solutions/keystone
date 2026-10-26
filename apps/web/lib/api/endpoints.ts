import { useAuth } from "@clerk/nextjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";

import { apiRequest } from "@/lib/api/client";
import {
  anomaliesSchema,
  billingStatusSchema,
  cashPositionSchema,
  connectionsSchema,
  guidanceQuestionsSchema,
  guidanceSummarySchema,
  healthSignalsSchema,
  obligationsSchema,
  payrollSummarySchema,
  runwaySchema,
  scenariosSchema,
  transactionsSchema,
} from "@/lib/api/schemas";

function useToken() {
  const { getToken } = useAuth();
  return async () => getToken();
}

export function useCashPosition() {
  const token = useToken();
  return useQuery({
    queryKey: ["cash-position"],
    queryFn: async () => apiRequest("/v1/dashboard/cash-position", cashPositionSchema, { token: await token() }),
  });
}

export function useRunway(days = 90, scenarioId?: string) {
  const token = useToken();
  const query = scenarioId ? `&scenario_id=${scenarioId}` : "";
  return useQuery({
    queryKey: ["runway", days, scenarioId],
    queryFn: async () =>
      apiRequest(`/v1/dashboard/runway?days=${days}${query}`, runwaySchema, {
        token: await token(),
      }),
  });
}

export function useObligations() {
  const token = useToken();
  return useQuery({
    queryKey: ["obligations"],
    queryFn: async () => apiRequest("/v1/dashboard/obligations", obligationsSchema, { token: await token() }),
  });
}

export function useTransactions(limit = 50) {
  const token = useToken();
  return useQuery({
    queryKey: ["transactions", limit],
    queryFn: async () =>
      apiRequest(`/v1/dashboard/transactions?limit=${limit}`, transactionsSchema, {
        token: await token(),
      }),
  });
}

export function useHealthSignals() {
  const token = useToken();
  return useQuery({
    queryKey: ["health-signals"],
    queryFn: async () => apiRequest("/v1/dashboard/health-signals", healthSignalsSchema, { token: await token() }),
  });
}

export function useAnomalies(limit = 20) {
  const token = useToken();
  return useQuery({
    queryKey: ["anomalies", limit],
    queryFn: async () => apiRequest(`/v1/monitoring/anomalies?limit=${limit}`, anomaliesSchema, { token: await token() }),
  });
}

export function useBillingStatus() {
  const token = useToken();
  return useQuery({
    queryKey: ["billing-status"],
    queryFn: async () => apiRequest("/v1/billing/status", billingStatusSchema, { token: await token() }),
  });
}

export function useConnections() {
  const token = useToken();
  return useQuery({
    queryKey: ["connections"],
    queryFn: async () => apiRequest("/v1/plaid/connections", connectionsSchema, { token: await token() }),
  });
}

export function useScenarios() {
  const token = useToken();
  return useQuery({
    queryKey: ["scenarios"],
    queryFn: async () => apiRequest("/v1/scenarios", scenariosSchema, { token: await token() }),
  });
}

export function usePayrollSummary() {
  const token = useToken();
  return useQuery({
    queryKey: ["payroll-summary"],
    queryFn: async () => apiRequest("/v1/payroll/summary", payrollSummarySchema, { token: await token() }),
  });
}

export function useGuidanceSummary() {
  const token = useToken();
  return useQuery({
    queryKey: ["guidance-summary"],
    queryFn: async () => apiRequest("/v1/guidance/summary", guidanceSummarySchema, { token: await token() }),
  });
}

export function useGuidanceQuestions() {
  const token = useToken();
  return useQuery({
    queryKey: ["guidance-questions"],
    queryFn: async () => apiRequest("/v1/guidance/questions", guidanceQuestionsSchema, { token: await token() }),
  });
}

export function useCreateScenario() {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      name: string;
      revenue_delta_pct: number;
      vendor_terms_shift_days: number;
      add_hire_role_id?: string;
    }) =>
      apiRequest("/v1/scenarios", z.any(), {
        method: "POST",
        body: payload,
        token: await token(),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["scenarios"] });
    },
  });
}

export function useCreateRole() {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      title: string;
      monthly_cost_cents: number;
      start_date?: string;
      is_planned?: boolean;
    }) =>
      apiRequest("/v1/payroll/roles", z.any(), {
        method: "POST",
        body: payload,
        token: await token(),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["payroll-summary"] });
    },
  });
}

export function useCreateCheckoutSession() {
  const token = useToken();
  return useMutation({
    mutationFn: async () =>
      apiRequest(
        "/v1/billing/checkout-session",
        z.object({ url: z.string().url() }),
        { method: "POST", token: await token() }
      ),
  });
}

export function useCreatePortalSession() {
  const token = useToken();
  return useMutation({
    mutationFn: async () =>
      apiRequest(
        "/v1/billing/portal-session",
        z.object({ url: z.string().url() }),
        { method: "POST", token: await token() }
      ),
  });
}

export function usePlaidLinkToken() {
  const token = useToken();
  return useQuery({
    queryKey: ["plaid-link-token"],
    queryFn: async () =>
      apiRequest("/v1/plaid/link-token", z.object({ link_token: z.string() }), {
        method: "POST",
        token: await token(),
      }),
  });
}

export function useExchangePlaidPublicToken() {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { public_token: string; institution_name?: string }) =>
      apiRequest("/v1/plaid/exchange", z.any(), {
        method: "POST",
        body: payload,
        token: await token(),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["connections"] });
    },
  });
}

export function useTriggerPlaidSync() {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { connection_id: string; days_back?: number }) =>
      apiRequest("/v1/plaid/sync", z.any(), {
        method: "POST",
        body: payload,
        token: await token(),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["connections"] });
    },
  });
}
