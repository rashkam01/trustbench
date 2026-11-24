from dataclasses import dataclass


@dataclass
class EvalCase:
    case_id: str
    question: str
    answerable: bool
    expected_article: str | None


@dataclass
class EvalResult:
    case_id: str
    question: str
    answerable: bool
    expected_article: str | None
    retrieved_articles: list[str]
    recall_hit: bool | None
    abstained: bool
    grounded: bool
    citations: list[tuple[str, str]]
    answer: str
    latency_ms: float
    prompt_tokens: int | None
    completion_tokens: int | None