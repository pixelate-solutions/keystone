from pydantic import BaseModel


class GuidanceSummaryResponse(BaseModel):
    summary: str
    key_drivers: list[str]


class GuidanceQuestionsResponse(BaseModel):
    questions: list[str]
