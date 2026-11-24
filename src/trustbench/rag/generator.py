import time
from dataclasses import dataclass
from typing import Protocol

from openai import OpenAI
from pydantic import BaseModel

from trustbench.config import settings
from trustbench.rag.retriever import RetrievedChunk

_client = OpenAI(api_key=settings.openai_api_key)


class Citation(BaseModel):
    chunk_id: str
    reference: str


class AnswerResponse(BaseModel):
    answer: str
    abstained: bool
    citations: list[Citation]


@dataclass
class GenerationResult:
    response: AnswerResponse
    latency_ms: float
    prompt_tokens: int | None
    completion_tokens: int | None


class Generator(Protocol):
    def generate(self, question: str, passages: list[RetrievedChunk]) -> GenerationResult: ...


SYSTEM_PROMPT = """You are a careful assistant answering questions about the EU AI Act using only the provided passages.
Rules:
- Only use information in the provided passages. Do not use outside knowledge.
- If the passages do not contain enough information to answer, set abstained=true, give a short explanation that you cannot answer from the provided context, and set citations to an empty list.
- If you can answer, set abstained=false, give the answer, and list every passage you relied on in citations, each with its chunk_id and its article reference (e.g. "Article 1").
- Never invent a chunk_id that is not listed in the passages below.
"""


class OpenAIGenerator:
    def generate(self, question: str, passages: list[RetrievedChunk]) -> GenerationResult:
        context = "\n\n".join(
            f"[chunk_id: {p.chunk_id}] ({p.article} - {p.title})\n{p.text}"
            for p in passages
        )
        user_prompt = f"Passages:\n{context}\n\nQuestion: {question}"

        start = time.monotonic()
        completion = _client.chat.completions.parse(
            model=settings.generation_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format=AnswerResponse,
        )
        latency_ms = (time.monotonic() - start) * 1000

        usage = completion.usage
        return GenerationResult(
            response=completion.choices[0].message.parsed,
            latency_ms=latency_ms,
            prompt_tokens=usage.prompt_tokens if usage else None,
            completion_tokens=usage.completion_tokens if usage else None,
        )