from trustbench.ingest.fetch_source import fetch
from trustbench.ingest.chunker import ParagraphChunker
from trustbench.ingest.embed import embed_texts
from trustbench.ingest.store import ensure_schema, upsert_document, upsert_chunks, get_connection


def main() -> None:
    text, provenance = fetch()

    chunker = ParagraphChunker()
    chunks = chunker.chunk(text)
    print(f"Chunked into {len(chunks)} chunks")

    embeddings = embed_texts([c.text for c in chunks])
    print(f"Embedded {len(embeddings)} chunks")

    doc_id = provenance["doc_id"]
    full_provenance = {
        **provenance,
        "embedding_model": "text-embedding-3-small",
        "chunking_config": {"strategy": "one-chunk-per-article"},
    }

    with get_connection() as conn:
        ensure_schema(conn)
        upsert_document(conn, doc_id, full_provenance)
        upsert_chunks(conn, doc_id, chunks, embeddings)

    print(f"Stored {len(chunks)} chunks for document '{doc_id}'")


if __name__ == "__main__":
    main()