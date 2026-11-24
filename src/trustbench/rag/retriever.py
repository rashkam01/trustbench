from dataclasses import dataclass
from typing import Protocol

from trustbench.ingest.embed import embed_texts
from trustbench.ingest.store import get_connection


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    article: str
    title: str
    distance: float


class Retriever(Protocol):
    def retrieve(self, question: str, k: int) -> list[RetrievedChunk]: ...


def _to_vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(x) for x in embedding) + "]"


class PgVectorRetriever:
    def retrieve(self, question: str, k: int) -> list[RetrievedChunk]:
        [query_embedding] = embed_texts([question])
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, text, metadata, embedding <=> %s::vector AS distance
                FROM chunks
                ORDER BY distance
                LIMIT %s
                """,
                (_to_vector_literal(query_embedding), k),
            )
            rows = cur.fetchall()
        return [
            RetrievedChunk(
                chunk_id=row[0],
                text=row[1],
                article=row[2]["article"],
                title=row[2]["title"],
                distance=row[3],
            )
            for row in rows
        ]