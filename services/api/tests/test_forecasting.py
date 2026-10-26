from app.services.forecasting import ForecastInputs, compute_runway


def test_compute_runway_reduces_cash_with_burn() -> None:
    runway_days, projected_end_cash, drivers = compute_runway(
        ForecastInputs(
            current_cash_cents=1_000_000,
            average_daily_net_cents=8_000,
            upcoming_obligations_cents=120_000,
            days=30,
            revenue_delta_pct=0,
            added_hire_monthly_cents=0,
        )
    )

    assert runway_days > 0
    assert projected_end_cash < 1_000_000
    assert len(drivers) == 4


def test_negative_revenue_delta_increases_burn() -> None:
    base_runway, _, _ = compute_runway(
        ForecastInputs(
            current_cash_cents=2_000_000,
            average_daily_net_cents=10_000,
            upcoming_obligations_cents=0,
            days=60,
            revenue_delta_pct=0,
            added_hire_monthly_cents=0,
        )
    )

    stressed_runway, _, _ = compute_runway(
        ForecastInputs(
            current_cash_cents=2_000_000,
            average_daily_net_cents=10_000,
            upcoming_obligations_cents=0,
            days=60,
            revenue_delta_pct=-20,
            added_hire_monthly_cents=0,
        )
    )

    assert stressed_runway < base_runway
