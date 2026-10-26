from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass
class GuidanceSnapshot:
    health_status: str
    runway_days: int
    anomalies_count: int
    obligation_pressure: bool


class GuidanceProvider:
    async def summary(self, snapshot: GuidanceSnapshot) -> tuple[str, list[str]]:
        raise NotImplementedError

    async def questions(self, snapshot: GuidanceSnapshot) -> list[str]:
        raise NotImplementedError


class MockGuidanceProvider(GuidanceProvider):
    async def summary(self, snapshot: GuidanceSnapshot) -> tuple[str, list[str]]:
        drivers: list[str] = []
        tone = "stable"

        if snapshot.runway_days < 90 or snapshot.health_status == "at_risk":
            tone = "strained"
            drivers.append("Runway is below 90 days in current trajectory.")

        if snapshot.anomalies_count:
            drivers.append(f"{snapshot.anomalies_count} recent anomalies warrant review.")

        if snapshot.obligation_pressure:
            drivers.append("Upcoming obligations are concentrated in the next 2 weeks.")

        summary = (
            "Current state is stable with manageable cash timing."
            if tone == "stable"
            else "Current state is strained; timing and spend controls matter this cycle."
        )

        if not drivers:
            drivers.append("Cash flow patterns have remained consistent week-over-week.")

        return summary, drivers

    async def questions(self, snapshot: GuidanceSnapshot) -> list[str]:
        prompts = [
            "Which obligations can be shifted without increasing execution risk?",
            "What hiring decisions are reversible in the next 30 days?",
            "Which recurring vendors have grown fastest over the last quarter?",
        ]
        if snapshot.runway_days < 120:
            prompts.insert(0, "Which near-term actions can extend runway by at least 30 days?")
        return prompts[:5]


class StubAIGuidanceProvider(GuidanceProvider):
    async def summary(self, snapshot: GuidanceSnapshot) -> tuple[str, list[str]]:
        # Placeholder until an external provider client is wired.
        fallback = MockGuidanceProvider()
        return await fallback.summary(snapshot)

    async def questions(self, snapshot: GuidanceSnapshot) -> list[str]:
        fallback = MockGuidanceProvider()
        return await fallback.questions(snapshot)


def get_guidance_provider() -> GuidanceProvider:
    if settings.feature_ai_guidance and settings.ai_provider != "mock" and settings.ai_api_key:
        return StubAIGuidanceProvider()
    return MockGuidanceProvider()
