#!/usr/bin/env python3
import json, pathlib

ALL = pathlib.Path("data/working/sample_50.jsonl")
ANN = pathlib.Path("data/annotated/train.jsonl")

def read_jsonl_ids(path: pathlib.Path):
    ids = []
    with path.open(encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            obj = json.loads(ln)
            ids.append(obj["id"])
    return ids

def read_done_ids(path: pathlib.Path):
    if not path.exists():
        return set()
    done = set()
    with path.open(encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            obj = json.loads(ln)
            done.add(obj["id"])
    return done

def main():
    all_ids = read_jsonl_ids(ALL)
    done = read_done_ids(ANN)
    pending = [i for i in all_ids if i not in done]
    print(f"Total sample: {len(all_ids)}")
    print(f"Annotated   : {len(done)}")
    print(f"Pending     : {len(pending)}")
    if pending:
        print("Next up:", ", ".join(pending[:8]))

if __name__ == "__main__":
    main()

