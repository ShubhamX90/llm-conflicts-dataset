#!/usr/bin/env python3
"""
Normalize the raw conflicts JSONL to a compact working JSONL:

Input : data/raw/conflicts.jsonl  (authors' file)
Output: data/working/conflicts_working.jsonl

Each output line:
{
  id, query, conflict_type, ref_answer (optional),
  docs: [{doc_id,title,url,snippet,date}]
}
"""
from __future__ import annotations
import json, pathlib, sys

RAW = pathlib.Path("data/raw/conflicts.jsonl")
OUT = pathlib.Path("data/working/conflicts_working.jsonl")

# mapping raw labels -> standardized labels
MAP = {
    "No conflict": "No conflict",
    "Complementary information": "Complementary",
    "Conflicting opinions and research outcomes": "Conflicting opinions",
    "Conflict due to outdated information": "Outdated",
    "Conflict due to misinformation": "Misinformation",
}

def main():
    if not RAW.exists():
        sys.exit(f"ERROR: {RAW} not found.")
    OUT.parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with RAW.open("r", encoding="utf-8") as fin, OUT.open("w", encoding="utf-8") as fout:
        for i, line in enumerate(fin):
            line = line.strip()
            if not line: 
                continue
            ex = json.loads(line)
            q = (ex.get("question") or ex.get("query") or "").strip()
            if not q:
                continue
            docs = []
            for j, d in enumerate((ex.get("search_results") or [])[:10]):
                snippet = (d.get("short_text") or d.get("snippet") or "").strip()
                docs.append({
                    "doc_id": f"d{j+1}",
                    "title":  (d.get("title") or "").strip(),
                    "url":    (d.get("url") or "").strip(),
                    "snippet": snippet,
                    "date":   (d.get("date") or "").strip(),
                })
            raw_type = (ex.get("conflict_type") or "").strip()
            item = {
                "id": f"ex_{i:04d}",
                "query": q,
                "conflict_type": MAP.get(raw_type, raw_type),
                "ref_answer": (ex.get("correct_answer") or "").strip() or None,
                "docs": docs,
            }
            fout.write(json.dumps(item, ensure_ascii=False) + "\n")
            n += 1
    print(f"Wrote {n} → {OUT}")

if __name__ == "__main__":
    main()
