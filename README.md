# Financial News Impact Analyzer - Multi-Agent System

## Overview

This project implements a sophisticated multi-agent system using Pydantic AI to analyze financial news articles and assess their market impact. The system consists of three specialized agents that work together to extract entities, analyze sentiment, and predict market impact.

## Architecture

### Agent Workflow
```
Financial Article Input
         ↓
    [Entity Agent] ← Extracts companies, tickers, investments
         ↓
   [Sentiment Agent] ← Analyzes emotional tone & confidence
         ↓
    [Impact Agent] ← Predicts market effects using combined data
         ↓
    Unified Output
```

### Agent Specializations

1. **Entity Extraction Agent**
   - Extracts structured financial data (companies, tickers, investments)
   - Focuses on factual information extraction
   - Returns standardized JSON format

2. **Sentiment Analysis Agent**
   - Analyzes emotional tone of financial news
   - Provides confidence scores for sentiment assessment
   - Independent of entity extraction for unbiased analysis

3. **Market Impact Agent**
   - Synthesizes entity and sentiment data
   - Predicts short-term and long-term market effects
   - Makes informed decisions based on combined intelligence

## Installation & Setup

### Prerequisites
- Python 3.8+
- Ollama running locally on port 11434
- Gemma3:1b model installed in Ollama

### Dependencies
```bash
pip install pydantic-ai pydantic-evals asyncio
```

### Model Setup
```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the required model
ollama pull gemma3:1b

# Start Ollama service
ollama serve
```

## Usage

### Running the Main Pipeline
```bash
python main.py
```

This will process all 5 test articles and output combined results.

### Running Evaluations
```bash
python evaluation.py
```

This will run comprehensive evaluations on all three agents with detailed metrics.

### Individual Agent Testing
```python
from agents.entity_extraction_agent import entity_extraction_agent
from agents.sentiment_analysis_agent import sentiment_analysis_agent
from agents.market_impact_agent import market_impact_agent

# Test individual agents
article = {
    "article_id": "TEST-001",
    "headline": "Your headline here",
    "content": "Your content here",
    "published_at": "2024-01-01T00:00:00Z"
}

# Run entity extraction
entity_result = await entity_extraction_agent(article).run(article)
```

## Project Structure

```
financial-news-analyzer/
├── main.py                      # Main pipeline orchestrator
├── agents/
│   ├── entity_extraction_agent.py    # Entity extraction specialist
│   ├── sentiment_analysis_agent.py   # Sentiment analysis specialist
│   ├── market_impact_agent.py        # Market impact predictor
│   └── main_model.py                 # Model configuration
├── evaluation/
│   ├── evaluation.py                 # Comprehensive evaluation suite
│   └── eval_models.py                # Pydantic validation models
├── docs/
│   ├── architecture.md               # System architecture details
│   ├── design_decisions.md           # Design rationale
│   ├── prompt_iterations.md          # Prompt engineering journey
│   └── test_case_analysis.md         # Interesting test behaviors
├── ai_chat_history.txt               # Development conversation log
├── what_didnt_work.md               # Challenges and solutions
└── README.md                        # This file
```

## Key Features

### Multi-Agent Coordination
- **Parallel Processing**: Agents can run independently where possible
- **Data Flow**: Structured information passing between agents
- **Conflict Resolution**: Market impact agent synthesizes conflicting signals

### Robust Evaluation
- **Accuracy Metrics**: Field-by-field comparison with ground truth
- **Type Validation**: Ensures output format consistency
- **Edge Case Testing**: Handles various article types and scenarios

### Error Handling
- **JSON Parsing**: Robust extraction from LLM outputs
- **Validation**: Pydantic models ensure data integrity
- **Graceful Degradation**: System continues functioning with partial data

## Performance Metrics

The system is evaluated on:
- **Entity Extraction Accuracy**: Precision of factual data extraction
- **Sentiment Classification**: Accuracy of positive/neutral/negative classification
- **Market Impact Prediction**: Consistency of short/long-term predictions
- **Overall System Coherence**: How well agents work together

## Sample Output

```json
{
  "article_id": "FIN-001",
  "published_at": "2024-10-22T16:00:00Z",
  "company": "Tesla",
  "ticker": "TSLA",
  "project": null,
  "investment_usd": null,
  "sector": null,
  "sentiment": "positive",
  "confidence_score": 0.8,
  "short_term": "positive",
  "long_term": "positive"
}
```