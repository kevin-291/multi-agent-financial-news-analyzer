# Prompt Iterations

## 2-3 Prompt Iterations Showing Improvement

### Iteration 1: Initial Entity Extraction Agent (Basic)
```python
# INITIAL VERSION - Too Generic
prompt = f"""
Extract financial entities from this article:
{article['headline']}
{article['content']}

Return JSON with company, ticker, and other details.
"""
```

**Problems with V1:**
- Vague instructions led to inconsistent outputs
- No explicit field requirements
- Agents hallucinated missing information
- No validation of ticker format

### Iteration 2: Enhanced Entity Extraction Agent (Structured)
```python
# IMPROVED VERSION - More Specific
prompt = f"""
You are an expert in financial entity extraction.

Extract from this article:
Headline: {article['headline']}
Content: {article['content']}

Return JSON with these exact fields:
- company: Company name
- ticker: Stock ticker (e.g., NASDAQ: TSLA)
- investment_usd: Investment amount in USD
- sector: Industry sector

Do not guess missing information.
"""
```

**Improvements in V2:**
- Clearer field definitions
- Explicit ticker format examples
- "Do not guess" instruction to reduce hallucination
- Structured input presentation

### Iteration 3: Final Entity Extraction Agent (Production-Ready)
```python
# CURRENT VERSION - Highly Precise
prompt = f"""
You are an expert in financial entity extraction.

Only use the given article headline and content. Do NOT hallucinate or reference external knowledge. If any detail is not explicitly mentioned, return "null" for that field.

Input article ID: {article['article_id']}
Input article headline: {article['headline']}
Input article content: {article['content']}
Input published date: {article['published_at']}

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

STRICT FORMAT (JSON only):
{
  "article_id": <string>,
  "published_at": <string>,
  "company": <string|null>,
  "ticker": <string|null>,
  "project": <string|null>,
  "investment_usd": <integer|null>,
  "sector": <string|null>
}
"""
```

**Key Improvements in V3:**
- **Explicit anti-hallucination**: "Do NOT hallucinate or reference external knowledge"
- **Precise field definitions**: Exact format requirements for each field
- **Concrete examples**: "$50 billion → 50000000000" for investment conversion
- **Strict output format**: JSON-only response with no explanations
- **Null handling**: Clear instructions for missing data
- **Input validation**: Copy article_id and published_at to ensure consistency