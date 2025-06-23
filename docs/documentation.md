## 📘 Project Documentation: Financial News Multi-Agent System

### 🏠 System Architecture – Why Multiple Agents?

The system uses a **multi-agent architecture** to simulate how financial analysts would logically break down and interpret market-relevant news. Each agent is specialized and focused, allowing for better control, transparency, and traceability of decisions.

**Agents:**
- **Entity Extraction Agent**: Parses the article to extract structured financial facts.
- **Sentiment Analysis Agent**: Evaluates the tone of the article.
- **Market Impact Agent**: Predicts short- and long-term impact based on facts and sentiment.

**Benefits of modular agents:**
- Easier debugging and evaluation.
- Individual prompt tuning and versioning.
- Agents can be reused across domains (e.g., news summarization, alerting).

---

### ⚙ Design Decisions & Rationale

| Design Component              | Decision & Justification |
|------------------------------|---------------------------|
| ✅ Agent Specialization        | Clear separation of logic improves reliability and explainability. |
| ✉ Prompt Chaining Architecture | Output of one agent feeds into the next, mirroring human reasoning. |
| 👁‍🗨 Strict JSON Response Format | Simplifies downstream integration and prevents parsing errors. |
| 📊 Regex JSON Extractor      | Handles edge cases like markdown-wrapped responses (```json ... ```). |
| 🚀 Pydantic-AI Integration    | Structured interface for managing multi-model backends and retries. |

---

### 💡 Prompt Iteration Examples

#### 🌐 Sentiment Agent

**Initial Prompt:**
```
Analyze the article and tell if it's good or bad.
```
**Issue:** Returned explanations, lacked structure.

**Mid Iteration:**
```
Output must be JSON with keys: "sentiment" and "confidence_score"
```
**Issue:** Still returned textual descriptions.

**Final Version:**
```txt
You are an expert financial sentiment analysis agent.
...
STRICT FORMAT (JSON only):
{
  "sentiment": "<positive|neutral|negative>",
  "confidence_score": <float>
}
```
✅ **Result**: Accurate, structured outputs, no leakage.

---

### 🚪 Examples of Interesting Test Case Behaviors

#### 1. **No Ticker Available**
- **Input**: "Apple surges on strong iPhone sales"
- **Output**: `"ticker": null`
- ✅ Correctly avoids assumption without (NASDAQ: AAPL).

#### 2. **High Investment Recognized**
- **Input**: "$50 billion investment"
- **Output**: `"investment_usd": 50000000000`
- ✅ Correct transformation and numerical extraction.

#### 3. **Mixed Signals Handled**
- **Input**: Positive earnings + CEO warning
- **Output**: `"sentiment": "neutral"`, `"confidence_score": 0.6`
- ✅ Shows nuanced understanding and mid-range confidence.

---