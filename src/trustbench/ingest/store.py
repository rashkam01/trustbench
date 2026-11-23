import psycopg
from psycopg.types.json import Jsonb
from trustbench.config import settings
from trustbench.ingest.chunker import Chunk

SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    doc_id TEXT PRIMARY KEY,
    source_url TEXT NOT NULL,
    regulation_id TEXT NOT NULL,
    consolidated_version TEXT,
    fetch_timestamp TIMESTAMPTZ NOT NULL,
    checksum TEXT NOT NULL,
    embedding_model TEXT NOT NULL,
    chunking_config JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    doc_id TEXT REFERENCES documents(doc_id),
    chunk_index INT NOT NULL,
    text TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    metadata JSONB NOT NULL,
    UNIQUE (doc_id, chunk_index)
);
"""


def ensure_schema(conn: psycopg.Connection) -> None:
    conn.execute(SCHEMA)
    conn.commit()


def upsert_document(conn: psycopg.Connection, doc_id: str, provenance: dict) -> None:
    conn.execute(
        """
        INSERT INTO documents (doc_id, source_url, regulation_id, consolidated_version,
                                fetch_timestamp, checksum, embedding_model, chunking_config)
        VALUES (%(doc_id)s, %(source_url)s, %(regulation_id)s, %(consolidated_version)s,
                %(fetch_timestamp)s, %(checksum)s, %(embedding_model)s, %(chunking_config)s)
        ON CONFLICT (doc_id) DO UPDATE SET
            checksum = EXCLUDED.checksum,
            fetch_timestamp = EXCLUDED.fetch_timestamp
        """,
        {**provenance, "doc_id": doc_id, "chunking_config": Jsonb(provenance["chunking_config"])},
    )
    conn.commit()


def upsert_chunks(conn: psycopg.Connection, doc_id: str, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    with conn.cursor() as cur:
        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = f"{doc_id}:{chunk.chunk_index:04d}"
            metadata = Jsonb({"article": chunk.article, "title": chunk.title})
            cur.execute(
                """
                INSERT INTO chunks (id, doc_id, chunk_index, text, embedding, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (doc_id, chunk_index) DO UPDATE SET
                    text = EXCLUDED.text,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata
                """,
                (chunk_id, doc_id, chunk.chunk_index, chunk.text, embedding, metadata),
            )
    conn.commit()


def get_connection() -> psycopg.Connection:
    return psycopg.connect(settings.database_url)