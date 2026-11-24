from dataclasses import dataclass

from trustbench.rag.generator import AnswerResponse
from trustbench.rag.retriever import RetrievedChunk


@dataclass
class ValidatedAnswer:
    answer: str
    abstained: bool
    citations: list[tuple[str, str]]
    grounded: bool


def validate(response: AnswerResponse, retrieved: list[RetrievedChunk]) -> ValidatedAnswer:
    retrieved_ids = {chunk.chunk_id for chunk in retrieved}
    citation_ids = {c.chunk_id for c in response.citations}

    if response.abstained:
        grounded = len(response.citations) == 0
    else:
        grounded = len(citation_ids) > 0 and citation_ids.issubset(retrieved_ids)

    return ValidatedAnswer(
        answer=response.answer,
        abstained=response.abstained,
        citations=[(c.chunk_id, c.reference) for c in response.citations],
        grounded=grounded,
    )