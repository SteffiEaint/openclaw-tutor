# AI Model Evaluation Plan

The project includes comparison of local and cloud AI models. This document provides a repeatable evaluation structure for the final technical report.

## Models/providers to consider

The project planning has mentioned alternatives including:

- Google Gemini;
- Ollama/local models;
- Groq;
- OpenRouter;
- other permitted providers discovered during the project.

The exact final model list should reflect what was actually tested.

## Evaluation dimensions

| Dimension | What to record |
|---|---|
| Task quality | Accuracy/relevance of progress summaries and recommendations |
| Response time | Time from request to usable response |
| Cost | Free-tier limits or measured API cost |
| Privacy | Whether educational data leaves the local environment |
| Reliability | Failures, rate limits, inconsistent outputs |
| Hardware | RAM/CPU/GPU requirements for local models |
| Integration | Ease of use with the project workflow |
| Output consistency | Whether repeated prompts produce stable results |

## Suggested test prompts

Use the same structured scenarios for every model. Examples:

1. Summarize a student's progress.
2. Identify overdue assignments.
3. Explain why a student may need attention.
4. Produce a concise teacher report.
5. Produce a supportive student reminder.

## Scoring

Use a simple 1–5 score for each dimension where a numerical comparison is useful. Keep qualitative notes alongside scores because a single number cannot capture privacy, cost, or integration trade-offs.

## Final interpretation

The goal is not to declare one model universally best. The goal is to identify which model is most appropriate for this prototype's tutoring tasks and explain the trade-offs between cloud performance, local privacy, cost, and operational complexity.
