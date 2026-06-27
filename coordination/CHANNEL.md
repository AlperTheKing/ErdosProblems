# Direct Agent Channel — Erdős #23  (Step-1 ⇄ Step-2)

Set up 2026-06-26 so **Step-1 (Claude)** and **Step-2 (Codex)** coordinate directly,
with no human relay. Both agents run in `E:\Projects\ErdosProblems` on a `/loop`.

## Roles
- **Step-1 (Claude)** — owns the single arXiv paper, the independent exact-verification
  gate, and the clean all-N assembly. Cut-pressure / KKT graphon route to δ=0.
- **Step-2 (Codex)** — owns the flag-LP certificate (δ) and the Γ-lemma / δ=0.
  Defect-augmented Γ route (master inequality Γ+D*≤N²; Defective Shell Extraction Lemma).

## Mailbox files (append-only)
- `coordination/STEP1_TO_STEP2.md` — **Step-1 WRITES, Step-2 READS** (messages *for* Step-2)
- `coordination/STEP2_TO_STEP1.md` — **Step-2 WRITES, Step-1 READS** (messages *for* Step-1)
- `coordination/CHANNEL.md` — this protocol (read once)

## Per `/loop` iteration, each agent does:
1. **READ** the `*_TO_<self>` file. Process every message block whose `[ISO]` stamp is
   newer than the last one you handled (track your last-seen stamp in your own PROGRESS
   log / memory).
2. If a reply is warranted, **APPEND** a block to `<self>_TO_<other>` (format below).
3. **Never edit or delete** the other agent's outbox, or the other agent's live-run files
   (`bridge/flagsdp/*` are Step-2's; `problems/23/writeup/*` + `arxiv/anc/` are Step-1's).
   Reading the other's files for audit is fine; writing/overwriting them is not. Append only.

## Message format (one block per message)
```
## [ISO-8601Z] STEP-1 -> STEP-2   (RE: [stamp], optional)
<body: facts, claims, questions. Gate every closure/bound claim on an EXACT check.>
---
```

## Shared discipline (both agents)
- The **EXACT rational Fraction certificate is the only closure gate** — 3 false closures
  in this project were caught only by it. Numeric "η<0 / promising / almost" is NOT a result.
- Commit as the **user alone** — no `Co-Authored-By: ... anthropic/claude` trailer (breaks
  the Google CLA).
- Compute **≤ 64–100 workers** (never 128), native clang++, never WSL.
- **English.** One claim per block; cite a file path / lemma / number / exact value.
