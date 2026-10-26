import pytest

from app.services.guidance import GuidanceSnapshot, MockGuidanceProvider


@pytest.mark.asyncio
async def test_mock_guidance_summary_and_questions() -> None:
    provider = MockGuidanceProvider()
    summary, drivers = await provider.summary(
        GuidanceSnapshot(
            health_status="stable",
            runway_days=130,
            anomalies_count=2,
            obligation_pressure=False,
        )
    )
    questions = await provider.questions(
        GuidanceSnapshot(
            health_status="strained",
            runway_days=75,
            anomalies_count=2,
            obligation_pressure=True,
        )
    )

    assert "state" in summary
    assert drivers
    assert len(questions) >= 3
