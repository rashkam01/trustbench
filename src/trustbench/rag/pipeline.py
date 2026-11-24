from dataclasses import dataclass

from trustbench.config import settings
from trustbench.rag.generator import Generator, GenerationResult, OpenAIGenerator
from trustbench.rag.retriever import PgVectorRetriever, Retriever, RetrievedChunk
from trustbench.rag.validation import ValidatedAnswer, validate


@dataclass
class PipelineResult:
    validated: ValidatedAnswer
    retrieved: list[RetrievedChunk]
    latency_ms: float
    prompt_tokens: int | None
    completion_tokens: int | None


class RAGPipeline:
    def __init__(
        self,
        retriever: Retriever | None = None,
        generator: Generator | None = None,
        k: int | None = None,
    ):
        self.retriever = retriever or PgVectorRetriever()
        self.generator = generator or OpenAIGenerator()
        self.k = k or settings.retrieval_k

    def answer(self, question: str) -> PipelineResult:
        retrieved = self.retriever.retrieve(question, self.k)
        generation = self.generator.generate(question, retrieved)
        validated = validate(generation.response, retrieved)
        return PipelineResult(
            validated=validated,
            retrieved=retrieved,
            latency_ms=generation.latency_ms,
            prompt_tokens=generation.prompt_tokens,
            completion_tokens=generation.completion_tokens,
        )