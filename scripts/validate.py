#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, sys

ANN = pathlib.Path("data/annotated/train.jsonl")

def read_jsonl(p):
    with p.open() as f:
        for line in f:
            if line.strip(): yield json.loads(line)

def main():
    if not ANN.exists():
        raise SystemExit(f"Missing {ANN}")
    ok = True
    for ex in read_jsonl(ANN):
        doc_ids = {d["doc_id"] for d in ex.get("docs", [])}
        noted = [n["doc_id"] for n in ex.get("notes", [])]
        if any(n not in doc_ids for n in noted):
            print(f"{ex['id']}: note refers to unknown doc_id", file=sys.stderr); ok=False
        supporting = {n["doc_id"] for n in ex.get("notes", []) if n.get("verdict") in {"supports","partial"}}
        abst = ex.get("final",{}).get("abstain", False)
        if not abst and not supporting:
            print(f"{ex['id']}: non-abstain but no supports/partial", file=sys.stderr); ok=False
        for d in ex.get("final",{}).get("evidence", []):
            if d not in supporting:
                print(f"{ex['id']}: evidence {d} not among supports/partial", file=sys.stderr); ok=False
    if not ok: raise SystemExit(1)
    print("Validation passed ✅")

if __name__ == "__main__":
    main()
