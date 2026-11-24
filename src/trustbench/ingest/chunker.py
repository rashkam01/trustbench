import re
from dataclasses import dataclass
from typing import Protocol

ARTICLE_HEADER = re.compile(r"(?m)^Article (\d+[a-z]?)\s*\n+([^\n]+)\n+")


@dataclass
class Chunk:
    chunk_index: int
    text: str
    article: str
    title: str


class Chunker(Protocol):
    def chunk(self, text: str) -> list[Chunk]: ...


class ParagraphChunker:
    def chunk(self, text: str) -> list[Chunk]:
        matches = list(ARTICLE_HEADER.finditer(text))
        chunks = []
        for i, match in enumerate(matches):
            article_num = match.group(1)
            title = match.group(2).strip().rstrip("'")
            body_start = match.end()
            body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[body_start:body_end].strip()
            chunks.append(
                Chunk(
                    chunk_index=i,
                    text=f"Article {article_num}\n{title}\n\n{body}",
                    article=f"Article {article_num}",
                    title=title,
                )
            )
        return chunks