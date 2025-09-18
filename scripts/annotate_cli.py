#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, textwrap, sys

# Input file: pass as first arg (e.g., data/working/sample_shubham.jsonl)
INP  = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("data/working/sample_50.jsonl")
# Output annotations + progress
OUT  = pathlib.Path("data/annotated/train.jsonl")
PROG = pathlib.Path("data/annotated/.progress.json")

VERDICT = {
  "1":"supports","2":"partial","3":"contradicts",
  "4":"irrelevant","5":"outdated","6":"misinformation"
}

STYLE = {
  "No conflict": "Give a single direct answer grounded in the most relevant passage(s). No hedging.",
  "Complementary": "Synthesize multiple valid facets; combine complementary details. Do not invent contradictions.",
  "Conflicting opinions": "Present the differing positions neutrally; attribute each stance; avoid picking a side unless recency/evidence quality clearly favors one.",
  "Outdated": "Prefer the most recent reliable data; you may note older values but clarify they are outdated.",
  "Misinformation": "Ignore incorrect claims; state the verified fact with reliable citations.",
}

def read_jsonl(p: pathlib.Path):
    # Force UTF-8 on Windows to avoid cp1252 decode errors
    with p.open("r", encoding="utf-8", errors="strict") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def save_progress(done_ids: set):
    PROG.parent.mkdir(parents=True, exist_ok=True)
    PROG.write_text(json.dumps({"done_ids": sorted(done_ids)}, indent=2), encoding="utf-8")

def load_progress() -> set:
    if PROG.exists():
        obj = json.loads(PROG.read_text(encoding="utf-8"))
        return set(obj.get("done_ids", []))
    return set()

def wrap(s, w=98):
    return "\n".join(textwrap.wrap(s or "", width=w))

def annotate(ex):
    notes = []
    for d in ex["docs"]:
        print("\n" + "-"*100)
        print(f"[{d['doc_id']}] {d.get('title') or '(no title)'}")
        if d.get("url"):  print(d["url"])
        if d.get("date"): print(f"date: {d['date']}")
        print(wrap(d.get("snippet","") or "(no snippet)"))

        v = input("Verdict 1 sup | 2 part | 3 contra | 4 irr | 5 old | 6 misinfo [default=4]: ").strip() or "4"
        if v not in VERDICT: v = "4"
        key = input("Key fact (short; optional): ").strip()
        quote = input("Optional short quote/span: ").strip()

        notes.append({
            "doc_id": d["doc_id"],
            "verdict": VERDICT[v],
            "key_fact": key,
            "quote": quote
        })

    ctype = ex["conflict_type"]
    style = STYLE.get(ctype, "")
    supp_ids = [n["doc_id"] for n in notes if n["verdict"] in {"supports","partial"}]

    print("\n" + "="*100)
    print("QUERY:", wrap(ex["query"]))
    print("\nStyle:", style)
    print("Supporting docs:", supp_ids or "(none)")

    while True:
        choice = input("[a]nswer  [u]nknown/abstain: ").strip().lower()
        if choice == "u":
            return {
              "id": ex["id"],
              "query": ex["query"],
              "conflict_type": ctype,
              "docs": ex["docs"],
              "notes": notes,
              "final": {
                  "style_hint": style,
                  "answer": "Unknown based on provided documents.",
                  "evidence": [],
                  "abstain": True
              },
              "trace_type": "summarized",
              "think": "<think>Per-doc notes then abstain because no support.</think>"
            }
        if choice == "a":
            ans = input("Write final answer (3–6 sentences):\n> ").strip()
            cites = []
            if supp_ids:
                cite_str = input("List evidence doc_ids separated by space (e.g., d2 d5), or empty: ").strip()
                cites = [t for t in cite_str.split() if t in supp_ids]
            return {
              "id": ex["id"],
              "query": ex["query"],
              "conflict_type": ctype,
              "docs": ex["docs"],
              "notes": notes,
              "final": {
                  "style_hint": style,
                  "answer": ans,
                  "evidence": cites,
                  "abstain": False
              },
              "trace_type": "summarized",
              "think": "<think>Summarized per-doc notes precede the final answer.</think>"
            }

def main():
    if not INP.exists():
        raise SystemExit(f"Input not found: {INP}\nPass an input file, e.g.\n  python scripts/annotate_cli.py data/working/sample_shubham.jsonl")

    done = load_progress()
    OUT.parent.mkdir(parents=True, exist_ok=True)

    items = [ex for ex in read_jsonl(INP) if ex["id"] not in done]
    print(f"{len(done)} already annotated, {len(items)} to go from {INP}.")

    for ex in items:
        print("\n" + "="*100)
        print(f"ID {ex['id']}  |  Type: {ex['conflict_type']}")
        print("QUERY:", wrap(ex["query"]))

        ann = annotate(ex)
        with OUT.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ann, ensure_ascii=False) + "\n")

        done.add(ex["id"])
        save_progress(done)
        print(f"Saved {ex['id']} ✔")

    print("All done ✅")

if __name__ == "__main__":
    main()
