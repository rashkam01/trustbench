# Decisions log

Dated, one decision per entry. Append-only.
XML wasn't offered and HTML was used instead — that satisfies the "document why HTML was selected" part of our resolved decision.

## 2026-11-23 — Source documents

- EU AI Act: Regulation (EU) 2024/1689, amended by Regulation (EU) 2026/1744.
  Consolidated version 27.07.2026 (001.001).
  https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02024R1689-20260727
  Only HTML/PDF offered on EUR-Lex (no XML) — using HTML as source format.
  Note: EUR-Lex text is a documentation tool with no legal effect; the authentic
  text is the Official Journal. Acceptable here since the regulations are test
  material, not legal advice (matches project scope).

- GDPR: Regulation (EU) 2016/679.
  Consolidated version 04.05.2016.
  https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02016R0679-20160504
  Only HTML/PDF offered on EUR-Lex (no XML) — using HTML as source format.

- Week 1 vertical slice ingests only the EU AI Act (Recitals + Articles 1–30).
  GDPR ingestion is deferred to the full-corpus build.