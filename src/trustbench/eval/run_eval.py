import json
from datetime import datetime, timezone
from pathlib import Path

from trustbench.config import settings
from trustbench.eval.models import EvalCase, EvalResult
from trustbench.rag.pipeline import RAGPipeline

CASES_FILE = Path("data/eval/slice_questions.jsonl")
RESULTS_DIR = Path("data/eval/results")


def load_cases() -> list[EvalCase]:
    cases = []
    for line in CASES_FILE.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        cases.append(
            EvalCase(
                case_id=row["id"],
                question=row["question"],
                answerable=row["answerable"],
                expected_article=row.get("expected_article"),
            )
        )
    return cases


def run_case(pipeline: RAGPipeline, case: EvalCase) -> EvalResult:
    result = pipeline.answer(case.question)
    retrieved_articles = [chunk.article for chunk in result.retrieved]

    recall_hit = None
    if case.answerable:
        recall_hit = case.expected_article in retrieved_articles

    return EvalResult(
        case_id=case.case_id,
        question=case.question,
        answerable=case.answerable,
        expected_article=case.expected_article,
        retrieved_articles=retrieved_articles,
        recall_hit=recall_hit,
        abstained=result.validated.abstained,
        grounded=result.validated.grounded,
        citations=result.validated.citations,
        answer=result.validated.answer,
        latency_ms=result.latency_ms,
        prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens,
    )


def main() -> None:
    cases = load_cases()
    pipeline = RAGPipeline()
    results = [run_case(pipeline, case) for case in cases]

    answerable_results = [r for r in results if r.answerable]
    recall_hits = sum(1 for r in answerable_results if r.recall_hit)
    recall_at_k = recall_hits / len(answerable_results) if answerable_results else None

    unanswerable_results = [r for r in results if not r.answerable]
    correct_abstentions = sum(1 for r in unanswerable_results if r.abstained and r.grounded)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = RESULTS_DIR / f"slice_run_{timestamp}.jsonl"
    with out_file.open("w") as f:
        for r in results:
            f.write(json.dumps(r.__dict__) + "\n")

    if recall_at_k is not None:
        print(f"Recall@{settings.retrieval_k}: {recall_hits}/{len(answerable_results)} = {recall_at_k:.2f}")
    print(f"Correct abstentions: {correct_abstentions}/{len(unanswerable_results)}")
    print(f"Results written to {out_file}")

    for r in results:
        status = "ABSTAIN" if r.abstained else "ANSWER"
        hit = "" if r.recall_hit is None else (" HIT" if r.recall_hit else " MISS")
        print(f"{r.case_id} [{status}{hit}] grounded={r.grounded} -> {r.retrieved_articles}")


if __name__ == "__main__":
    main()