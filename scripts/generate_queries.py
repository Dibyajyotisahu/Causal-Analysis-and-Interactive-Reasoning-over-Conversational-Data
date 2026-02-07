import csv
import json
from collections import defaultdict

DATA_PATH = "data/processed/normalized_conversations.json"
OUT_CSV = "queries.csv"

def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Build per-outcome examples
    by_outcome = defaultdict(list)
    for c in data:
        by_outcome[c["outcome"]].append(c["call_id"])

    rows = []
    qid = 1
    for outcome, call_ids in by_outcome.items():
        # diverse query templates
        templates = [
            f"Why did the outcome '{outcome}' occur?",
            f"What factors contributed to '{outcome}'?",
            f"Which turns serve as evidence for '{outcome}' and why?",
        ]
        for t in templates:
            rows.append({
                "Query_Id": qid,
                "Query": t,
                "Query_Category": "task1" if "Why did" in t else "followup",
                "System_Output": "",
                "Remarks": f"Target outcome={outcome}, example_call_ids={';'.join(call_ids[:3])}"
            })
            qid += 1

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Query_Id", "Query", "Query_Category", "System_Output", "Remarks"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Wrote {len(rows)} queries to {OUT_CSV}")

if __name__ == "__main__":
    main()
