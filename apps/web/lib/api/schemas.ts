import { z } from "zod";

export const cashPositionSchema = z.object({
  amount_cents: z.number(),
  currency_code: z.literal("USD"),
  as_of: z.string().datetime(),
});

export const runwayDriverSchema = z.object({
  label: z.string(),
  impact_cents: z.number(),
  detail: z.string(),
});

export const runwaySchema = z.object({
  days_requested: z.number(),
  runway_days: z.number(),
  projected_end_cash_cents: z.number(),
  currency_code: z.literal("USD"),
  drivers: z.array(runwayDriverSchema),
});

export const obligationSchema = z.object({
  obligation_id: z.string(),
  type: z.enum(["payroll", "vendor", "debt"]),
  name: z.string(),
  amount_cents: z.number(),
  currency_code: z.literal("USD"),
  due_date: z.string(),
  cadence: z.string().nullable().optional(),
  notes: z.string().nullable().optional(),
});

export const obligationsSchema = z.object({
  items: z.array(obligationSchema),
});

export const transactionItemSchema = z.object({
  txn_id: z.string(),
  date: z.string(),
  name: z.string(),
  amount_cents: z.number(),
  currency_code: z.literal("USD"),
  merchant: z.string().nullable().optional(),
  category: z.string().nullable().optional(),
  is_pending: z.boolean(),
});

export const transactionCategorySchema = z.object({
  category: z.string(),
  total_cents: z.number(),
  transaction_count: z.number(),
});

export const transactionsSchema = z.object({
  items: z.array(transactionItemSchema),
  categories: z.array(transactionCategorySchema),
});

export const healthSignalSchema = z.object({
  label: z.enum(["stable", "strained", "at_risk"]),
  summary: z.string(),
  reason: z.string(),
});

export const healthSignalsSchema = z.object({
  status: z.enum(["stable", "strained", "at_risk"]),
  signals: z.array(healthSignalSchema),
  changed_since_last_week: z.string(),
});

export const anomalySchema = z.object({
  anomaly_id: z.string(),
  type: z.string(),
  severity: z.enum(["low", "medium", "high"]),
  confidence: z.enum(["low", "medium", "high"]),
  title: z.string(),
  explanation: z.string(),
  detected_at: z.string().datetime(),
  related_txn_ids: z.array(z.string()),
});

export const anomaliesSchema = z.array(anomalySchema);

export const connectionSchema = z.object({
  connection_id: z.string(),
  institution: z.string().nullable().optional(),
  status: z.enum(["pending", "syncing", "ready", "error"]),
  last_error: z.string().nullable().optional(),
  last_sync_at: z.string().datetime().nullable().optional(),
});

export const connectionsSchema = z.array(connectionSchema);

export const billingStatusSchema = z.object({
  tier: z.string(),
  subscription_status: z.string(),
  current_period_end: z.string().datetime().nullable(),
  portal_available: z.boolean(),
});

export const scenarioSchema = z.object({
  scenario_id: z.string(),
  name: z.string(),
  revenue_delta_pct: z.number(),
  vendor_terms_shift_days: z.number(),
  add_hire_role_id: z.string().nullable().optional(),
  created_at: z.string().datetime(),
});

export const scenariosSchema = z.array(scenarioSchema);

export const payrollSummarySchema = z.object({
  baseline_monthly_cents: z.number(),
  fully_loaded_multiplier: z.number(),
  planned_hires_monthly_cents: z.number(),
  payroll_pct_of_revenue: z.number(),
  can_hire_until: z.string().nullable(),
});

export const guidanceSummarySchema = z.object({
  summary: z.string(),
  key_drivers: z.array(z.string()),
});

export const guidanceQuestionsSchema = z.object({
  questions: z.array(z.string()),
});

export type CashPosition = z.infer<typeof cashPositionSchema>;
export type Runway = z.infer<typeof runwaySchema>;
export type Obligations = z.infer<typeof obligationsSchema>;
export type Transactions = z.infer<typeof transactionsSchema>;
export type HealthSignals = z.infer<typeof healthSignalsSchema>;
export type Anomaly = z.infer<typeof anomalySchema>;
export type Connection = z.infer<typeof connectionSchema>;
export type BillingStatus = z.infer<typeof billingStatusSchema>;
export type Scenario = z.infer<typeof scenarioSchema>;
export type PayrollSummary = z.infer<typeof payrollSummarySchema>;
