#!/usr/bin/env python3
"""
Compute simple metrics over annotated data.
"""
import json, collections, pathlib

ANN = pathlib.Path("data/annotated/train.jsonl")

def read_jsonl(p):
    with p.open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def main():
    if not ANN.exists():
        raise SystemExit("No annotations yet.")
    cnt_type = collections.Counter()
    abst = 0
    sup = 0
    total_notes = 0
    for ex in read_jsonl(ANN):
        cnt_type[ex["conflict_type"]] += 1
        s = sum(n["verdict"] in {"supports","partial"} for n in ex.get("notes",[]))
        sup += s
        total_notes += len(ex.get("notes",[]))
        if ex.get("final",{}).get("abstain"):
            abst += 1
    print("Per-type counts:", dict(cnt_type))
    print("Total examples:", sum(cnt_type.values()))
    print("Abstains:", abst)
    print("Avg supporting/total notes:", round(sup/max(1,total_notes),3))

if __name__ == "__main__":
    main()
