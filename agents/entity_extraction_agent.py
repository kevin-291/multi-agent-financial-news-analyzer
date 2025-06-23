from pydantic_ai import Agent
from .main_model import model

ollama_model = model()

def entity_extraction_agent(article) -> Agent:
    
  prompt = f"""
  You are an expert in financial entity extraction.

  Only use the given article headline and content. Do NOT hallucinate or reference external knowledge. If any detail is not explicitly mentioned, return "null" for that field.

  Input article ID:
  {article['article_id']}

  Input article headline:
  {article['headline']}

  Input article content:
  {article['content']}

  Input published date:
  {article['published_at']}

  REQUIREMENTS:
  • Extract and return a JSON object with exactly the following fields:
      - "article_id": The article's ID (copy from input)
      - "published_at": The article's publish date (copy from input)
      - "company": Name of the company mentioned (if clearly stated)
      - "ticker": Official stock ticker (only if explicitly written like "(NASDAQ: TSLA)")
      - "project": Name of the investment project or initiative (if directly named)
      - "investment_usd": Total USD investment mentioned as an integer (e.g., $50 billion → 50000000000)
      - "sector": Industry or domain mentioned (e.g., AI, biotech, cloud) — only if stated directly in text
  • Do NOT infer or guess any values.
  • Do NOT include any extra keys, explanations, or assumptions.
  • If any field is not mentioned, return "None" for that field.

  Note: Your output will be used by other agents. Ensure precision.

  STRICT FORMAT (JSON only):

  {{
    "article_id": <string>,
    "published_at": <string>,
    "company": <string|null>,
    "ticker": <string|null>,
    "project": <string|null>,
    "investment_usd": <integer|null>,
    "sector": <string|null>
  }}
  """

  agent = Agent(model=ollama_model, instructions=prompt)
  return agent




