from pydantic_ai import Agent
from .main_model import model

ollama_model = model()

def sentiment_analysis_agent(article) -> Agent:
    prompt = f"""
    You are an expert financial sentiment analysis agent.
    Analyze only the sentiment based on the given headline and content. Do not assume or hallucinate context. Do not use external sources.

    Input article headline:
    {article['headline']}

    Input article content:
    {article['content']}

    REQUIREMENTS:
    • Output must be valid JSON with exactly two keys:
        - "sentiment": Must be one of ["positive", "neutral", "negative"]
        - "confidence_score": A float with one decimal place between 0.0 and 1.0
    • Do NOT include explanations, assumptions, or unrelated text.

    Note: Your output will complement the entity extraction and market impact agents.

    STRICT FORMAT (JSON only):

    {{
      "sentiment": "<positive|neutral|negative>",
      "confidence_score": <float>
    }}
    """
  
    agent = Agent(model=ollama_model, instructions=prompt)
    return agent

