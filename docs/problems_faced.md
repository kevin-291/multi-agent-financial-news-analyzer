# What Didn't Work and Why

## 1. **Hallucination Control Was Much Harder Than Expected**

**What I Tried**: Simple instructions like "don't make up information" and "only use the provided text."

**Why It Failed**: The model would still infer tickers from company names (e.g., assuming Apple → AAPL), make up investment amounts based on "industry standards," and assign sectors based on general knowledge rather than article content.

**What Actually Worked**: Triple-layered approach:
- Explicit warnings about external knowledge
- "Return null for missing data" requirements  
- Concrete examples of what constitutes "explicitly mentioned"

**Unexpected Discovery**: Even with perfect instructions, ~2% hallucination rate persisted—some level of model creativity seems unavoidable.

## 2. **JSON Format Consistency Was a Nightmare**

**What I Tried**: Standard instruction "return valid JSON" with a template.

**Why It Failed**: Models would:
- Add explanatory text before/after JSON
- Include extra fields not in the template
- Use inconsistent null representations ("null", "None", "N/A", empty strings)
- Break JSON with unescaped quotes in content

**Solution That Worked**: "STRICT FORMAT (JSON only)" with exact template and multiple format examples. Still required robust parsing with regex cleanup.

**Ongoing Challenge**: Even with perfect prompts, occasional format breaks require defensive programming.

## 3. **Market Impact Agent Initially Made Nonsensical Predictions**

**What I Tried**: Direct article analysis for market impact prediction.

**Why It Failed**: The agent lacked crucial context. It would predict positive short-term impact for regulatory warnings or negative impact for revenue growth—because it missed the semantic nuances that entity and sentiment agents could provide.

**Solution**: Created structured input combining sentiment confidence scores with entity data. Impact predictions became dramatically more coherent.

**Key Insight**: Complex reasoning tasks need preprocessed, structured inputs—not raw text.

## 4. **Evaluation Ground Truth Was Harder to Define Than Expected**

**What I Tried**: Binary right/wrong evaluation for each field.

**Why It Failed**: Financial analysis often has defensible variations:
- Is "biotech" the same as "biotechnology"?
- Should Tesla's sector be "automotive" or "clean energy"?
- How do you score partially correct sentiment confidence (0.7 vs 0.8)?

**Compromise Solution**: Exact-match evaluation for objective fields (tickers, amounts) and acceptable-variation handling for subjective fields (sectors, sentiment confidence).

**Remaining Challenge**: Ground truth reflects my interpretation—real-world financial analysts might disagree.

## 5. **Async Coordination Created Subtle Race Conditions**

**What I Tried**: Full parallelization of all three agents for maximum speed.

**Why It Failed**: Market Impact Agent would occasionally receive incomplete or malformed data from the other agents due to timing issues and JSON parsing failures happening asynchronously.

**Solution**: Strategic parallelization—Entity and Sentiment agents run in parallel, then Market Impact Agent runs sequentially with validated inputs.

**Lesson**: Performance optimization must respect data dependencies.

## 6. **Local Model Performance Was Frustratingly Inconsistent**

**What I Tried**: Using Gemma3:1b for cost-effective local development.

**Challenges Encountered**:
- Model would perform differently across runs with identical inputs
- Complex prompts sometimes caused the model to freeze or return empty responses
- Numerical conversion (like "$50 billion" → 50000000000) was unreliable

**Mitigation Strategies**:
- Extensive prompt testing and validation
- Robust error handling and retry logic
- Conservative model assumptions (return null when uncertain)

**Trade-off Accepted**: Chose consistency and reliability over potentially higher accuracy from larger models.

## 7. **Cross-Agent Information Flow Initially Lost Context**

**What I Tried**: Simple JSON passing between agents.

**Why It Subtly Failed**: Market Impact Agent would make decisions without understanding the confidence level of the input data. A low-confidence positive sentiment should be treated differently than high-confidence positive sentiment.

**Solution**: Enriched the inter-agent communication protocol to include metadata like confidence scores and uncertainty indicators.

**Insight**: Multi-agent systems need rich communication protocols, not just data exchange.

## 8. **Performance vs. Accuracy Trade-offs Were Non-Linear**

**Unexpected Discovery**: Adding more detailed prompts improved accuracy but significantly increased processing time and occasionally caused the local model to produce lower-quality outputs due to context length limitations.

**Finding**: There was a sweet spot in prompt complexity—too simple led to inconsistent outputs, too complex overwhelmed the model.

**Current Status**: Settled on moderately complex prompts that balance accuracy, consistency, and performance, but recognize this might need adjustment for different model sizes/capabilities.