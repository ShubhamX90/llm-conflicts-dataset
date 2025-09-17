#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, random, collections

WORK = pathlib.Path("data/working/conflicts_working.jsonl")
SAMP = pathlib.Path("data/working/sample_50.jsonl")
IDS  = pathlib.Path("data/working/sample_50_ids.json")

TARGET = {
  "No conflict": 10,
  "Complementary information": 10,
  "Conflicting opinions and research outcomes": 10,
  "Conflict due to outdated information": 10,
  "Conflict due to misinformation": 10,
}

def read_jsonl(p):
    with p.open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def main():
    data = list(read_jsonl(WORK))
    by = collections.defaultdict(list)
    for ex in data:
        by[ex["conflict_type"]].append(ex)

    rng = random.Random(7)
    picked = []
    for c, k in TARGET.items():
        pool = by.get(c, [])
        if not pool: continue
        k = min(k, len(pool))
        picked.extend(rng.sample(pool, k))

    if len(picked) < 50:
        seen = {ex["id"] for ex in picked}
        rest = [ex for ex in data if ex["id"] not in seen]
        picked.extend(rng.sample(rest, 50 - len(picked)))

    SAMP.write_text("\n".join(json.dumps(ex, ensure_ascii=False) for ex in picked) + "\n")
    IDS.write_text(json.dumps([ex["id"] for ex in picked], indent=2))
    print(f"Saved {len(picked)} → {SAMP}")
    print(f"IDs → {IDS}")

if __name__ == "__main__":
    if not WORK.exists():
        raise SystemExit(f"Missing {WORK}. Run prepare_from_raw.py first.")
    main()
