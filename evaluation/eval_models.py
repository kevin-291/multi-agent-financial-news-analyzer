from pydantic import BaseModel, Field

class EntityOutput(BaseModel):
    article_id: str
    published_at: str
    company: str | None
    ticker: str | None
    project: str | None
    investment_usd: int | None
    sector: str | None

class SentimentOutput(BaseModel):
    sentiment: str = Field(..., pattern='^(positive|neutral|negative)$')
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class ImpactOutput(BaseModel):
    short_term: str = Field(..., pattern='^(positive|neutral|negative)$')
    long_term: str = Field(..., pattern='^(positive|neutral|negative)$')
