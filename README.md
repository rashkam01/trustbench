# TrustBench

**A test lab for AI assistants: how well do they answer, and can they be trusted to act?**

> **Status: in progress (planning and Week 1).** This README describes what is being built and how it will be measured. No results have been measured yet, so every results table below is intentionally empty. Feedback is very welcome (see [Feedback wanted](#feedback-wanted)).

---

## In plain words

Many AI demos look impressive, but few show **proof** that the system works. TrustBench builds two small AI systems on top of European data-protection law and then **measures them honestly**:

1. **An assistant that answers questions** about the EU AI Act and the GDPR, and says "I can't find this in the documents" when that is the truth.
2. **An assistant that takes action**: it reads a data-breach report, decides what the law requires, saves a record with the legal deadline to a database, and drafts a notification. A human has to approve before anything becomes final.

The law is only the test material. **The product is the measurement**: clear scores, written failure analysis and no invented numbers.

> This is an engineering study, not legal advice.

## Why this exists

- An AI that sounds confident but is wrong is a risk, especially in regulated areas.
- An AI that can **change things** (write to a database, send a message) needs a stricter test than one that only answers questions.
- Most projects stop at "it works on my example". TrustBench asks: how often, in which cases, how fast, at what cost, and what happens when it fails?

---

## What it does: a worked example

### Part 1: the question-answering assistant (RAG)

RAG stands for *retrieval-augmented generation*. In everyday terms, it is an **open-book exam**: the AI first looks up the relevant passages, then writes an answer based only on what it found.

| Question | What a good system does |
|---|---|
| "Within how many hours must a company report a personal data breach?" | Finds the GDPR breach-notification article, answers "72 hours, to the supervisory authority" and cites the passage. |
| "What are the penalties under the Digital Services Act?" | That law is **not** in the documents, so the correct behaviour is to say it cannot answer. Inventing a number counts as a serious failure. |

### Part 2: the breach-triage agent

An **agent** is an AI that can choose steps and use tools instead of only writing text. This one handles a breach report like this (illustrative session):

```
Report:   "A laptop with 2,000 customers' names and emails, not encrypted,
           was stolen last night."

Agent:    1. Searches the regulation for the breach-notification rule.
          2. Asks: "When did you first become aware of the loss?"
          3. Decides: notification to the authority is required, deadline
             is 72 hours after awareness.
          4. Prepares an incident record (deadline, risk level, cited articles)
             with status PENDING_APPROVAL.
          5. Drafts the notification text.

Human:    Reviews and clicks "approve".
System:   Record becomes final.
```

Four example scenarios show what the agent is tested on (the real, human-labelled set lives in the repo's data folder):

| Scenario | Expected behaviour |
|---|---|
| Unencrypted laptop with customer names and emails stolen | Notification to the authority required; record with deadline created |
| Laptop was fully encrypted and the key is safe | Reporting to the authority may not be needed, but the incident must still be documented internally |
| "We think someone may have accessed a mailbox, but we're not sure" | Ask for the missing facts instead of guessing |
| An internal lunch menu leaked | Not a personal-data breach; no notification record |

All scenarios are **synthetic**. No real personal data is used.

---

## How it works

```mermaid
flowchart LR
    U["Incident report or question"] --> A["Agent<br/>(LangGraph)"]
    A -->|"calls tools through MCP"| M["MCP server"]
    M --> T1["search_regulations"]
    M --> T2["get_article"]
    M --> T3["create_incident"]
    M --> T4["draft_notification"]
    T1 --> V[("Law texts<br/>pgvector")]
    T2 --> V
    T3 --> P[("PostgreSQL<br/>incident records")]
    A --> H{"Human approval"}
    H -->|approved| P
    A -.->|"every step recorded"| L["Langfuse traces"]
```

**Safety rules built into the design:**
- The agent can act only through the listed tools.
- Every database write starts as `pending_approval` and needs a human to approve it.
- Each write has a unique key, so a retry cannot create a duplicate record.
- The agent has a step limit and a cost limit.
- The agent only drafts notifications. Nothing is sent anywhere.

## The tools, in simple language

| Tool | What it is | What it does here |
|---|---|---|
| **Python** | A programming language | Everything is written in it |
| **FastAPI** | A framework for web services | Exposes the system as an API with a minimal approval step |
| **Pydantic** | A data-checking library | Makes sure data has the expected shape (for example, a deadline is really a date) |
| **PostgreSQL** | A database | Stores incident records |
| **pgvector** | A PostgreSQL add-on for search by meaning | Finds the passages related to a question even when the words differ |
| **MCP (Model Context Protocol)** | A standard "plug" for giving AI apps access to tools | Publishes the four tools above so any compatible AI app can use them |
| **LangGraph** | A framework for running an agent as a set of steps | The "harness" around the AI: runs the loop, keeps state, enforces limits and the approval gate |
| **Langfuse** | A tracing tool | Records every step so failures can be diagnosed |
| **Docker** | Packages the app so it runs the same everywhere | Reproducible setup and deployment |
| **GitHub Actions** | Automatic checks on every change | Runs tests and evaluations in CI |

---

## How "good" is measured

**Part 1: question answering**

| What | How |
|---|---|
| Did search find the right passage? | **Recall@K**: the share of questions where the correct passage is in the top K results |
| Is the answer correct and backed by the source? | Verdicts with written definitions: supported / partially supported / unsupported |
| Does it admit when it does not know? | Correct abstention / wrong answer / missed abstention |
| Speed and cost | Latency and token cost per question |

An AI "judge" may help with grading, but it is **calibrated first**: its grades are compared with about 30 answers labelled by hand, and the agreement is reported. The same model never generates and judges.

**Part 2: the agent**

| What | How |
|---|---|
| Right decision and deadline? | Exact comparison with the expected outcome |
| Right tool, right arguments? | Tool-call accuracy |
| Correct database record? | Field-by-field comparison |
| Safe? | Counts of writes without approval, duplicate records, errors, limit breaches |
| Asks instead of guessing? | Checked on scenarios with missing facts |
| Speed and cost | Steps, latency and cost per scenario |

**Rules for honest reporting**
- Expected answers are written by hand and traced to a specific source passage.
- Unanswerable questions are re-checked against the documents.
- Datasets are versioned and every change is logged.
- Nothing is reported that does not come from a recorded, reproducible run.
- A small test set cannot prove universal truths, so limitations are reported next to the numbers.

---

## What the finished project will contain

- A public repository with documented code, an architecture diagram and a live demo
- A results table comparing RAG configurations (chunking, vector vs hybrid search, reranking)
- A results table for the agent on about 20 scenarios
- An MCP server with documented tools
- A written analysis of where and why each system fails
- A technical report and a short community write-up

**Results (to be filled in from recorded runs):**

| RAG configuration | Recall@K | Correct answers | Missed abstentions | Latency | Cost |
|---|---|---|---|---|---|
| Baseline | not yet measured | not yet measured | not yet measured | not yet measured | not yet measured |

| Agent | Correct decisions | Correct records | Unapproved writes | Steps | Cost |
|---|---|---|---|---|---|
| Breach-triage agent | not yet measured | not yet measured | not yet measured | not yet measured | not yet measured |

## Roadmap

| Week | Focus |
|---|---|
| 1 | Dataset and baseline: one working end-to-end slice first, then the full corpus, about 60 questions, evaluation script, tracing, CI. Also: about 20 breach scenarios and tool contracts. |
| 2 | Retrieval experiments, plus an MCP server with read-only tools |
| 3 | Answer evaluation and judge calibration, plus write tools, incident table and the agent with its approval gate |
| 4 | Agent evaluation, failure analysis, deployment, report |

Checkpoint at the end of Week 3: if behind, the number of scenarios is reduced. MCP, the agent and the approval step are not dropped.

## Out of scope

Fine-tuning, a general chatbot, an elaborate frontend, multi-agent systems, sending real emails or notifications, real personal data, and any commercial or legal-advice claims.

## Repository layout (planned)

```
docs/        plan, architecture, evaluation rules
data/        questions, scenarios, labels (versioned)
src/         retrieval, evaluation, MCP server, agent
configs/     experiment settings, so runs are reproducible
reports/     results and failure analysis
```

## Quick start

Coming once the first end-to-end slice runs (Week 1). Instructions will be added here.

---

## Feedback wanted

If you are reviewing this README, a few honest answers would help a lot:

1. **Clarity:** could you explain this project to a colleague after reading it once? Where did you get lost?
2. **Scope:** is this realistic in four weeks? What would you cut or simplify?
3. **Evaluation:** are the measurements convincing? What would you add or distrust?
4. **Agent design:** is the breach-triage use case and its approval gate a sensible choice for showing safe agent behaviour?

Please open an issue or message me directly.

## Disclaimer

TrustBench is a technical study. The EU AI Act and GDPR are used as test material. Nothing in this repository is legal advice, and the expected outcomes in the datasets are test labels, not legal opinions.

## Author and license

Built by [your name], Berlin. [Link to LinkedIn or contact]
License: [to be chosen, for example MIT]