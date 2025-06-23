from pydantic_ai import Agent
from .main_model import model

ollama_model = model()

def market_impact_agent(context) -> Agent:
    
    prompt = f"""
    You are a financial market impact analysis agent.
    Assess the likely short-term and long-term impact of the news on the company's stock performance.

    You are provided:
    - Headline: {context['headline']}
    - Content: {context['content']}
    - Sentiment: {context['sentiment']}
    - Confidence Score: {context['confidence_score']}
    - Sector: {context['sector']}
    - Investment Amount: {context['investment_usd']}

    Use these inputs strictly. Do not hallucinate or assume any details. If the impact is unclear, return "neutral".

    REQUIREMENTS:
    • Output must be valid JSON with exactly two fields:
        - "short_term": One of ["positive", "neutral", "negative"]
        - "long_term": One of ["positive", "neutral", "negative"]
    • Base judgment strictly on the inputs above.
    • Do NOT include any explanations, justifications, or unrelated keys.

    Note: This agent uses and integrates inputs from both entity and sentiment agents.

    STRICT FORMAT (JSON only):

    {{
      "short_term": "<positive|neutral|negative>",
      "long_term": "<positive|neutral|negative>"
    }}
    """

    agent = Agent(model=ollama_model, instructions=prompt)
    return agent

