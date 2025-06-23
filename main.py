import asyncio
import json
import re
from agents.entity_extraction_agent import entity_extraction_agent
from agents.sentiment_analysis_agent import sentiment_analysis_agent
from agents.market_impact_agent import market_impact_agent


def extract_json_from_response(text: str) -> dict:
    """
    Extract the JSON block from an LLM output string.
    Handles cases where the output is wrapped in ```json ... ``` or plain JSON.
    """
    # Remove wrapping ```json or ``` if present
    text = text.strip()
    if text.startswith("```json") or text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    # Extract the JSON block with a basic check
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}\nRaw text: {text}")

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

async def run_all_agents(article):
   
    entity_data = extract_json_from_response((await entity_extraction_agent(article).run(article)).output)
    
    sentiment_data = extract_json_from_response((await sentiment_analysis_agent(article).run(article)).output)

    impact_context = {
        "headline": article["headline"],
        "content": article["content"],
        "sentiment": sentiment_data["sentiment"],
        "confidence_score": sentiment_data["confidence_score"],
        "sector": entity_data["sector"],
        "investment_usd": entity_data["investment_usd"]
    }

    market_data = extract_json_from_response((await market_impact_agent(impact_context).run(impact_context)).output)

    combined_output = {
        **entity_data,
        **sentiment_data,
        **market_data
    }

    return combined_output

async def run_batch():
    results = await asyncio.gather(*(run_all_agents(article) for article in articles))
    print("\nBatch Processing Results:\n")
    for result in results:
        print(result)


if __name__ == "__main__":
    # To run batch processing:
    asyncio.run(run_batch())
