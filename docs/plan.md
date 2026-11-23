# TrustBench: project plan

> Canonical plan. Scope is frozen; changes only at the Friday review and are logged in the change log.

## What this is
An evaluation project and toolkit for RAG and agentic systems. An engineering study comparing a conventional regulatory RAG system (EU AI Act + GDPR as the test corpus) with an agentic variant, using calibrated evaluation, measurable performance and human-led failure diagnosis.

Stack: Python, FastAPI, Pydantic, PostgreSQL/pgvector, Langfuse, Docker, GitHub Actions. LangGraph agent is conditional (see Gate).

## Not in scope
Fine-tuning, a generic chatbot, an elaborate frontend, supporting every agent framework, commercial or platform claims. The regulations are test material, not the product; this is not legal advice.

## Design rules
- Build the concrete RAG evaluation first. Add abstractions only where experiments need swappable parts (chunker, retriever, reranker, model).
- One shared interface so the RAG system and the agent are scored on the same dataset with the same methodology.
- Failure diagnosis is done manually; automate only if the sample size justifies it.
- Never report invented numbers. Everything in the report comes from a recorded, reproducible run.

## Measurement rules
- Numbers for things measured directly: Recall@K, latency, token cost.
- Categorical verdicts with written definitions for answer quality: supported / partially supported / unsupported; correct / wrong / missed abstention.
- Report uncertainty and limitations. A small evaluation set does not establish universal truths.
- LLM judge: calibrate against ~30 human-labelled answers and report agreement; do not use the same model to generate and judge.

## Dataset rules
- Questions, expected answers and supporting passages are human-authored and traceable to a specific source passage.
- Unanswerable questions must genuinely be unanswerable from the corpus; re-check each against the documents.
- The dataset is versioned; every change to a question or label is logged.

## Milestones
**Week 1: dataset and baseline.** Build a vertical slice first (one document ingested, one question retrieves passages, one answer cites evidence or abstains, one evaluation run produces a result). Then: full corpus, 60 questions (incl. ~10 unanswerable), eval harness with Recall@K, Langfuse tracing, Docker and CI skeleton, README and architecture diagram. External review of README, plan and baseline.
**Week 2: retrieval experiments.** Chunking strategies, vector vs hybrid retrieval, reranking; Recall@K, latency, cost; reproducible runs from config files.
**Week 3: answer evaluation.** Correctness, faithfulness, abstention; hand-label ~30 answers; calibrate the judge; start the failure taxonomy while labelling.
**Gate (end of Week 3):** build the agent comparison only if all Week 3 deliverables are complete.
**Week 4: analysis and delivery.** Manual failure analysis; deployment; Docker and CI; Langfuse; technical report and README. If the gate is met: LangGraph agent vs conventional RAG on the same dataset.

## Done criteria
Public repo and live URL; one results table comparing configurations; one manual failure analysis; one technical report; a short write-up for the community. Anything not on this list is not built.

## Change log
- v1: scope frozen.
- v1 (2026-11-18): added v1 clarifications addendum (no scope change).

## Addendum (v1 clarifications, 2026-11-18)
Part of the frozen v1 scope.

- Results table: completes without the agent. Rows: chunking variants x {vector, hybrid, hybrid+rerank}.
  Columns: Recall@K, latency, cost, % correct, % grounded, % correct abstention.
  Agent rows are added only if the Week 3 gate is passed.
- Dataset: ~20 dev questions (for debugging) and ~40 test questions (not evaluated until
  configs are frozen). Stable question IDs, versioned dataset. Expected answers change only
  for factual or label errors, never because a model disagrees; each change bumps the version.
- Verdicts: correctness, groundedness and abstention are assessed separately.
  Correct but ungrounded = groundedness failure.
- Build order: vertical slice -> measure -> Langfuse -> Docker -> CI.
- Report must state: what was tested and why, what improved, what got worse,
  where the system failed, and what would change in production.
- Keep docs/decisions.md and a results log from day one so the report writes itself.

## Source documents
- EU AI Act: Regulation (EU) 2024/1689, consolidated 27.07.2026.
- GDPR: Regulation (EU) 2016/679, consolidated 04.05.2016.
See docs/decisions.md (2026-11-23) for exact URLs and format notes.