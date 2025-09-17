llm-conflicts-dataset

Human-annotated reasoning traces for conflict-aware RAG (Week-1 deliverable).

This repo contains:

Raw DRAGed-into-Conflicts dataset (JSONL, 458 Qs)

Working normalized JSONL

A balanced 50 sample (oversampling constrained by class availability)

An interactive annotator to produce per-doc reasoning + final grounded answers

Validation & metrics utilities

Collaboration setup for two annotators (Mac + Windows)

1) Repo layout
llm-conflicts-dataset/
  data/
    raw/                  # original files (read-only)
      conflicts.jsonl
    working/              # normalized / sampled subsets
      conflicts_working.jsonl
      sample_50.jsonl
      sample_50_ids.json
      sample_shubham.jsonl
      sample_shiv.jsonl
    annotated/            # human annotations
      train.jsonl
      .progress.json
  prompts/
    notes.txt             # per-doc verdict prompt (for future auto-draft)
    answer.txt            # final answer style prompt (for future auto-draft)
  scripts/
    prepare_from_raw.py   # raw -> normalized working jsonl
    sample_50.py          # balanced ~50 sampler (no duplicates)
    annotate_cli.py       # interactive annotation CLI
    validate.py           # sanity checks on annotations
    metrics.py            # quick counts & ratios

2) Environment setup

Python 3.12 recommended. Apple Silicon (arm64) wheels supported.

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -U pip setuptools wheel
pip install "pandas>=2,<3" "orjson>=3.10,<4" "pydantic>=2,<3" tqdm


zsh tip: quote globs ("pydantic>=2,<3") so * isn’t expanded by the shell.

3) Data flow (what & why)
3.1 Normalize raw → working

Why: unify field names and conflict labels, keep top-10 docs, de-couple from raw quirks.

python scripts/prepare_from_raw.py
# writes data/working/conflicts_working.jsonl (≈458 lines)


Standardized schema (one JSON per line):

{
  "id": "ex_0000",
  "query": "…",
  "conflict_type": "No conflict|Complementary|Conflicting opinions|Outdated|Misinformation",
  "ref_answer": "… or null",
  "docs": [
    {"doc_id":"d1","title":"…","url":"…","snippet":"…","date":"…"},
    ...
  ]
}

3.2 Sample a balanced 50

Why: small, diverse, human-quality set for week-1.

python scripts/sample_50.py
# writes data/working/sample_50.jsonl + sample_50_ids.json


Targets 10 per class, but never duplicates.

If a class is scarce (e.g., Misinformation has 5), it picks all and tops up others to reach 50.

Prints actual counts.

4) Annotation (reasoning traces)

Goal: For each query + 10 retrieved docs, produce:

Per-doc notes

verdict ∈ {supports, partial, contradicts, irrelevant, outdated, misinformation}

key_fact (short), optional quote

Final answer (3–6 sentences)

Use only docs marked supports/partial

Conflict-type style:

No conflict: direct answer

Complementary: synthesize facets

Conflicting opinions: present both sides with citations

Outdated: prefer newest evidence

Misinformation: ignore false, state verified fact

Inline citations like [d3][d7]

Or abstain: Unknown based on provided documents.

4.1 Split work (two annotators)

We pre-split:

data/working/sample_shubham.jsonl
data/working/sample_shiv.jsonl

4.2 Run the annotator
# Shubham:
python scripts/annotate_cli.py data/working/sample_shubham.jsonl

# Shiv (Windows):
python scripts\annotate_cli.py data\working\sample_shiv.jsonl


Saves to data/annotated/train.jsonl (appends one record per example).

Tracks done IDs in data/annotated/.progress.json.

Do 5–10 examples first, validate, then continue in chunks.

5) Validation & metrics
5.1 Validate
python scripts/validate.py


Checks:

Non-abstain must have ≥1 supports/partial note.

final.evidence doc_ids ⊆ {supports, partial}.

Notes reference valid doc_ids.

5.2 Metrics
python scripts/metrics.py


Prints:

Counts per conflict type

Total examples annotated

#Abstains

Avg (supports / total notes)

Use these in weekly slides.

6) Collaboration (Git/GitHub)

Initial push (done):

Repo: https://github.com/ShubhamX90/llm-conflicts-dataset

Auth: Personal Access Token (PAT), not password.

Daily flow:

Always git pull before starting.

Annotate a small batch (e.g., 5).

Then:

git add data/annotated/train.jsonl data/annotated/.progress.json
git commit -m "annotated N examples (yourname)"
git push


Teammate runs git pull to sync.

If both touched the same ID (shouldn’t happen with pre-split): resolve by keeping the better/most complete line in train.jsonl.

7) Quality checklist (quick)

Mark misinformation sparingly; only when you can justify with other docs.

Use outdated for older but once-correct values superseded by newer ones.

If no supports/partial → abstain.

Final answer must cite only supports/partial docs.

3–6 sentences is ideal; no fluff; grounded language.

Run validate.py before pushing.

8) Repro summary (one-liners)
# 0) env
python -m venv .venv && source .venv/bin/activate
python -m pip install -U pip setuptools wheel
pip install "pandas>=2,<3" "orjson>=3.10,<4" "pydantic>=2,<3" tqdm

# 1) normalize
python scripts/prepare_from_raw.py

# 2) sample
python scripts/sample_50.py

# 3) annotate (pick your file)
python scripts/annotate_cli.py data/working/sample_shubham.jsonl
# or
python scripts/annotate_cli.py data/working/sample_shiv.jsonl

# 4) validate + metrics
python scripts/validate.py
python scripts/metrics.py

9) Known gotchas

zsh globbing: quote * in version specs.

GitHub auth: use PAT (Settings → Developer settings → Tokens classic → repo).

Windows paths: use backslashes (\) in paths; Python accepts both in most cases.

Terminal width: the annotator wraps text; enlarge window for better readability.

10) Roadmap (after Week-1)

Optional auto-draft mode (LLM suggests notes; humans edit).

Export to SFT/DPO formats for fine-tuning.

Plug into TrustScore / TrustAlign evaluation pipeline on conflicts & “no-answer” sets.

Extend beyond conflicts to multi-hop and no-answer categories.

Contact: Shubham & Shiv — annotate in small batches, validate, and push.

