# Design Decisions and Rationale

## Core Design Philosophy

### 1. **Explicit Over Implicit**

**Decision**: All agents are instructed to return `null` for unknown values rather than making assumptions.

**Rationale**: 
- Financial analysis requires high precision
- False positives can be more damaging than acknowledged unknowns
- Downstream systems need to know the difference between "not mentioned" and "explicitly negative"

**Example**: If a ticker isn't explicitly stated as "(NASDAQ: TSLA)", the agent returns `null` rather than guessing based on company name.

**Alternative Considered**: Inference-based extraction using external knowledge
**Why Rejected**: Creates dependency on external data sources and reduces system reliability

### 2. **Separation of Analysis Dimensions**

**Decision**: Split sentiment and entity extraction into completely separate agents.

**Rationale**:
- **Cognitive independence**: A company can have great news (positive sentiment) but unclear financial details (sparse entities)
- **Bias prevention**: Entity extraction shouldn't be influenced by emotional tone
- **Specialized optimization**: Each agent can be tuned for its specific task

**Example**: "Tesla's revolutionary breakthrough" (positive sentiment) vs "Tesla's $50B investment" (factual entity) require different analytical approaches.

**Alternative Considered**: Single agent with multi-task prompting
**Why Rejected**: Risk of sentiment bias affecting factual extraction and vice versa

### 3. **Synthesis Agent for Complex Reasoning**

**Decision**: Create a dedicated market impact agent that combines outputs from other agents.

**Rationale**:
- **Contextual reasoning**: Market impact depends on multiple factors simultaneously
- **Domain expertise**: Financial market prediction requires specialized knowledge
- **Data integration**: Complex decisions need structured input from multiple sources

**Implementation**:
```python
impact_context = {
    "sentiment": sentiment_data["sentiment"],
    "confidence_score": sentiment_data["confidence_score"],
    "sector": entity_data["sector"],
    "investment_usd": entity_data["investment_usd"]
}
```

**Alternative Considered**: Rule-based combination of agent outputs
**Why Rejected**: Financial markets are too complex for simple rules; need LLM reasoning

## Technical Architecture Decisions

### 4. **Async Processing with Strategic Parallelization**

**Decision**: Run entity and sentiment agents in parallel, then synthesize with impact agent.

**Rationale**:
- **Efficiency**: Independent tasks should run concurrently
- **Logical dependency**: Impact prediction requires both sentiment and entity data
- **Resource optimization**: Maximize throughput while respecting dependencies

**Implementation Pattern**:
```python
# Parallel independent analysis
entity_task = entity_extraction_agent(article).run(article)
sentiment_task = sentiment_analysis_agent(article).run(article)

# Sequential synthesis
entity_result = await entity_task
sentiment_result = await sentiment_task
impact_result = await market_impact_agent(combined_context).run()
```

**Alternative Considered**: Full sequential processing
**Why Rejected**: Unnecessary performance penalty for independent tasks

### 5. **JSON-First Communication Protocol**

**Decision**: All inter-agent communication uses structured JSON with strict validation.

**Rationale**:
- **Type safety**: Pydantic models catch errors early
- **API compatibility**: JSON output can be easily consumed by other systems
- **Debugging clarity**: Structured data is easier to inspect and validate

**Implementation**:
```python
class EntityOutput(BaseModel):
    article_id: str
    published_at: str
    company: str | None
    ticker: str | None
    # ... with strict type checking
```

**Alternative Considered**: Natural language communication between agents
**Why Rejected**: Prone to parsing errors and ambiguity

## Prompt Engineering Decisions

### 6. **Strict Output Format Enforcement**

**Decision**: Use detailed format specifications with examples in every prompt.

**Rationale**:
- **Consistency**: Reduces variance in output format
- **Parsing reliability**: Structured formats are easier to parse programmatically
- **Error reduction**: Clear expectations reduce hallucination

**Example Pattern**:
```
STRICT FORMAT (JSON only):
{
  "article_id": <string>,
  "published_at": <string>,
  "company": <string|null>,
  ...
}
```

**Alternative Considered**: Natural language outputs with post-processing
**Why Rejected**: Introduces parsing complexity and error potential

### 7. **Explicit Hallucination Prevention**

**Decision**: Multiple warnings against external knowledge use in every prompt.

**Rationale**:
- **Data integrity**: Analysis should be based solely on provided article
- **Reproducibility**: Same input should always produce same output
- **Transparency**: Clear what information the analysis is based on

**Implementation Examples**:
- "Only use the given article headline and content"
- "Do NOT hallucinate or reference external knowledge"
- "If any detail is not explicitly mentioned, return 'null'"

**Alternative Considered**: Allow general financial knowledge
**Why Rejected**: Makes system non-deterministic and harder to validate

## Evaluation Framework Decisions

### 8. **Multi-Metric Evaluation Approach**

**Decision**: Implement both type validation and accuracy metrics.

**Rationale**:
- **Comprehensive assessment**: Different aspects of performance need different metrics
- **Error categorization**: Distinguish between format errors and content errors
- **Development feedback**: Multiple metrics provide better debugging information

**Metrics Implemented**:
- `IsInstance`: Validates output type and structure
- `AccuracyEvaluator`: Field-by-field accuracy comparison
- Custom accuracy calculation with partial credit

**Alternative Considered**: Single accuracy score
**Why Rejected**: Doesn't provide enough detail for system improvement

### 9. **Ground Truth Design Philosophy**

**Decision**: Create realistic but consistent ground truth data for evaluation.

**Rationale**:
- **Objective evaluation**: Need clear right/wrong answers
- **Consistency testing**: Same input should produce same output
- **Performance tracking**: Enables measurement of improvements over time

**Ground Truth Examples**:
```python
expected_entities = {
    "FIN-003": EntityOutput(
        company="Amazon", 
        ticker="AMZN", 
        project="Project Olympus",
        investment_usd=50000000000  # $50 billion
    )
}
```

**Alternative Considered**: Human expert evaluation
**Why Rejected**: Too slow for development iteration; saved for final validation

## Error Handling and Resilience Decisions

### 10. **Graceful Degradation Strategy**

**Decision**: System continues operating even with partial failures.

**Rationale**:
- **Reliability**: Better to provide partial results than complete failure
- **User experience**: Partial information is often still valuable
- **System robustness**: Real-world systems must handle edge cases

**Implementation**:
- Null values for missing information
- Continue processing even if one agent fails
- Clear error messages with context

**Alternative Considered**: Fail-fast approach
**Why Rejected**: Too brittle for production financial analysis system

### 11. **Input Validation at Every Stage**

**Decision**: Validate data format and content at each agent boundary.

**Rationale**:
- **Error localization**: Know exactly where problems occur
- **Data integrity**: Ensure each agent receives valid input
- **Debugging efficiency**: Faster problem identification and resolution

**Implementation Pattern**:
```python
def extract_json_from_response(text: str) -> dict:
    """Robust JSON extraction with detailed error messages"""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}\nRaw text: {text}")
```

## Model and Infrastructure Decisions

### 12. **Local Model Deployment**

**Decision**: Use local Ollama deployment rather than API-based models.

**Rationale**:
- **Cost control**: No per-request charges during development
- **Privacy**: Financial data stays local
- **Development speed**: No rate limits or network dependencies
- **Reproducibility**: Consistent model versions

**Trade-offs Accepted**:
- Setup complexity for end users
- Potentially lower model quality than latest API models
- Hardware requirements

**Alternative Considered**: OpenAI/Anthropic APIs
**Why Rejected**: Cost and privacy concerns for financial data

### 13. **Single Model Architecture**

**Decision**: Use the same base model (gemma3:1b) for all agents.

**Rationale**:
- **Consistency**: Reduces variables in system behavior
- **Resource efficiency**: Single model to manage and optimize
- **Deployment simplicity**: Fewer dependencies

**Trade-offs**:
- May not be optimal for each specific task
- Single point of failure for model-related issues

**Alternative Considered**: Specialized models for each agent
**Why Rejected**: Increased complexity without clear benefit for this use case

## Future-Proofing Decisions

### 14. **Modular Agent Design**

**Decision**: Each agent is completely independent and replaceable.

**Rationale**:
- **Evolutionary architecture**: Individual agents can be upgraded independently
- **A/B testing**: Can compare different implementations
- **Technology flexibility**: Agents could use different models or approaches

**Implementation**:
- Standardized input/output interfaces
- No shared state between agents
- Clear API boundaries

### 15. **Extensible Evaluation Framework**

**Decision**: Design evaluation system to easily accommodate new metrics and test cases.

**Rationale**:
- **Continuous improvement**: Easy to add new evaluation criteria
- **Comparative analysis**: Can evaluate different agent versions
- **Research enablement**: Supports experimentation with new approaches

These design decisions reflect a balance between immediate functionality and long-term maintainability, with particular attention to the unique requirements of financial data analysis where accuracy and transparency are paramount.
