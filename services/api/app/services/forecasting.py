from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ForecastInputs:
    current_cash_cents: int
    average_daily_net_cents: int
    upcoming_obligations_cents: int
    days: int
    revenue_delta_pct: int = 0
    added_hire_monthly_cents: int = 0


def compute_runway(inputs: ForecastInputs) -> tuple[int, int, list[dict[str, int | str]]]:
    baseline_burn = max(0, inputs.average_daily_net_cents)
    obligations_daily = int(inputs.upcoming_obligations_cents / max(inputs.days, 1))
    revenue_adjustment = int(-(baseline_burn * inputs.revenue_delta_pct) / 100)
    hire_daily = int(inputs.added_hire_monthly_cents / 30)

    adjusted_daily_burn = max(1, baseline_burn + obligations_daily + revenue_adjustment + hire_daily)
    runway_days = int(inputs.current_cash_cents / adjusted_daily_burn)
    projected_end_cash = inputs.current_cash_cents - adjusted_daily_burn * inputs.days

    drivers = [
        {
            "label": "Baseline burn",
            "impact_cents": baseline_burn,
            "detail": "Trailing average daily net outflow.",
        },
        {
            "label": "Upcoming obligations",
            "impact_cents": obligations_daily,
            "detail": "Scheduled obligations distributed across selected horizon.",
        },
        {
            "label": "Revenue scenario",
            "impact_cents": revenue_adjustment,
            "detail": "Revenue delta impact from scenario assumptions.",
        },
        {
            "label": "Added hire cost",
            "impact_cents": hire_daily,
            "detail": "Planned role monthly cost converted to daily impact.",
        },
    ]

    return runway_days, projected_end_cash, drivers
