import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dataclasses import dataclass
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, IsInstance
from eval_models import EntityOutput, SentimentOutput, ImpactOutput
from agents.entity_extraction_agent import entity_extraction_agent
from agents.sentiment_analysis_agent import sentiment_analysis_agent
from agents.market_impact_agent import market_impact_agent
from agents.main_model import model
from main import extract_json_from_response


ollama_model = model()

articles = [
    {
        "article_id": "FIN-001",
        "headline": "Tesla crushes Q3 expectations with record profits, but Musk warns of 'turbulent'",
        "content": "Tesla (NASDAQ: TSLA) reported stunning Q3 results with earnings of $1.05 per share",
        "published_at": "2024-10-22T16:00:00Z"
    },
    {
        "article_id": "FIN-002",
        "headline": "Small biotech CureGen soars on FDA approval, analysts remain skeptical",
        "content": "CureGen (NASDAQ: CURE), a small-cap biotech, received FDA approval for its novel",
        "published_at": "2024-11-01T14:30:00Z"
    },
    {
        "article_id": "FIN-003",
        "headline": "Amazon announces 'transformational' AI venture, but at massive cost",
        "content": "Amazon (NASDAQ: AMZN) unveiled Project Olympus, a $50 billion investment in AGI",
        "published_at": "2024-09-15T09:00:00Z"
    },
    {
        "article_id": "FIN-004",
        "headline": "Regional bank FirstState posts record earnings amid industry turmoil",
        "content": "FirstState Bank (NYSE: FSB) reported record Q2 earnings of $3.20 per share, up 45%",
        "published_at": "2024-10-12T10:30:00Z"
    },
    {
        "article_id": "FIN-005",
        "headline": "China tech giant ByteDance reports stellar growth, regulatory clouds remain",
        "content": "ByteDance, TikTok's parent company, leaked financials show revenue grew 70% to $12",
        "published_at": "2024-11-21T18:45:00Z"
    }
]


# 2️⃣ Define the custom evaluator
@dataclass
class AccuracyEvaluator(Evaluator[dict, dict, None]):
    def evaluate(self, ctx: EvaluatorContext[dict, dict, None]) -> float:
        out = ctx.output
        exp = ctx.expected_output
        if not isinstance(out, dict) or not isinstance(exp, dict):
            return 0.0
        # count correct fields
        total = len(exp)
        if total == 0:
            return 1.0  # avoid division by zero

        correct = 0
        for key, expected_value in exp.items():
            if key in out and out[key] == expected_value:
                correct += 1

        return correct / total

# 🔹 Ground truth expected outputs
expected_entities = {
    "FIN-001": EntityOutput(article_id="FIN-001",published_at="2024-10-22T16:00:00Z", company="Tesla", ticker="TSLA", project=None, investment_usd=None, sector=None).model_dump(mode="json"),
    "FIN-002": EntityOutput(article_id="FIN-002",published_at="2024-11-01T14:30:00Z", company="CureGen", ticker="CURE", project=None, investment_usd=None, sector="biotech").model_dump(mode="json"),
    "FIN-003": EntityOutput(article_id="FIN-003",published_at="2024-09-15T09:00:00Z", company="Amazon", ticker="AMZN", project="Project Olympus", investment_usd=50000000000, sector="AI").model_dump(mode="json"),
    "FIN-004": EntityOutput(article_id="FIN-004",published_at="2024-10-12T10:30:00Z", company="FirstState Bank", ticker="FSB", project=None, investment_usd=None, sector="banking").model_dump(mode="json"),
    "FIN-005": EntityOutput(article_id="FIN-005",published_at="2024-11-21T18:45:00Z", company="ByteDance", ticker=None, project=None, investment_usd=None, sector="tech").model_dump(mode="json")
}

expected_sentiments = {
    aid: SentimentOutput(sentiment="positive", confidence_score=1.0).model_dump(mode='json')
    for aid in expected_entities
}

expected_impacts = {
    aid: ImpactOutput(short_term="positive", long_term="positive").model_dump(mode='json')
    for aid in expected_entities
}

# 🔹 Build test cases
entity_cases = [
    Case(
        name=art["article_id"],
        inputs=art,
        expected_output=expected_entities[art["article_id"]],
        evaluators=[IsInstance(type_name="dict"), AccuracyEvaluator()]
    )
    for art in articles
]


sentiment_cases = [
    Case(
        name=art["article_id"], 
        inputs=art, 
        expected_output=expected_sentiments[art["article_id"]], 
        evaluators=[IsInstance("dict"), AccuracyEvaluator()]
        ) 
        for art in articles
]

impact_cases = []

for art in articles:
    aid = art["article_id"]
    sent = expected_sentiments[aid]
    ent = expected_entities[aid]
    impact_input = {
        "headline": art["headline"],
        "content": art["content"],
        **sent,
        "sector": ent["sector"],
        "investment_usd": ent["investment_usd"]
    }
    impact_cases.append(
        Case(
            name=aid,
            inputs=impact_input,
            expected_output=expected_impacts[aid],
            evaluators=[IsInstance(type_name="dict"), AccuracyEvaluator()]
        )
    )


ds_entity = Dataset(cases=entity_cases)
ds_sentiment = Dataset(cases=sentiment_cases)
ds_impact = Dataset(cases=impact_cases)

# 🔹 Pipeline runner
async def run_pipeline(article):
    e = extract_json_from_response((await entity_extraction_agent(article).run(article)).output)
    s = extract_json_from_response((await sentiment_analysis_agent(article).run(article)).output)
    ctx = {
        "headline": article["headline"],
        "content": article["content"],
        "sentiment": s["sentiment"],
        "confidence_score": s["confidence_score"],
        "sector": e["sector"],
        "investment_usd": e["investment_usd"]
    }
    m = extract_json_from_response((await market_impact_agent(ctx).run(ctx)).output)
    return {"entity": e, "sentiment": s, "impact": m}

async def run_entity(a): return (await run_pipeline(a))["entity"]
async def run_sentiment(a): return (await run_pipeline(a))["sentiment"]
async def run_impact(impact_input): 
    return extract_json_from_response((await market_impact_agent(impact_input).run(impact_input)).output)

# Evaluate all
async def evaluate_all():
    for label, ds, runner in [
        ("Entity Agent", ds_entity, run_entity),
        ("Sentiment Agent", ds_sentiment, run_sentiment),
        ("Market Impact Agent", ds_impact, run_impact)
    ]:
        print(f"\n=== {label} Evaluation ===")
        report = await ds.evaluate(runner, max_concurrency=2)
        report.print(include_input=True, include_output=True, include_expected_output=True)


if __name__ == "__main__":
    asyncio.run(evaluate_all()) 