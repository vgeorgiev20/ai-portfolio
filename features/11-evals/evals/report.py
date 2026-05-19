import json
import os
from datetime import datetime
import pandas as pd
from tabulate import tabulate


RESULTS_DIR = "results"
PASS_THRESHOLD = 0.7


def save_and_print(results: list[dict]) -> str:
    """Save full results to JSON and print a summary table. Returns output file path."""

    # Save full JSON report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(RESULTS_DIR, f"eval_run_{timestamp}.json")

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    # Build summary rows
    rows = []
    for r in results:
        scores = r["scores"]
        faith = scores["faithfulness"]["score"]
        relev = scores["relevance"]["score"]
        recall = scores["context_recall"]["score"]
        avg = (faith + relev + recall) / 3
        passed = "✓" if avg >= PASS_THRESHOLD else "✗"

        rows.append({
            "ID": r["id"],
            "Category": r["category"],
            "Faith": f"{faith:.2f}",
            "Relev": f"{relev:.2f}",
            "Recall": f"{recall:.2f}",
            "Avg": f"{avg:.2f}",
            "Pass": passed,
        })

    df = pd.DataFrame(rows)

    # Aggregate averages
    numeric = pd.DataFrame([{
        "faith": r["scores"]["faithfulness"]["score"],
        "relev": r["scores"]["relevance"]["score"],
        "recall": r["scores"]["context_recall"]["score"],
    } for r in results])

    avg_faith = numeric["faith"].mean()
    avg_relev = numeric["relev"].mean()
    avg_recall = numeric["recall"].mean()
    overall_avg = (avg_faith + avg_relev + avg_recall) / 3
    pass_rate = sum(1 for r in rows if r["Pass"] == "✓") / len(rows) * 100

    # Print
    print("\n")
    print("=" * 65)
    print("  EVAL RESULTS — tenancy.pdf (NSW Residential Tenancies Act)")
    print("=" * 65)
    print(tabulate(df, headers="keys", tablefmt="rounded_outline", showindex=False))
    print()
    print(f"  Averages:   Faithfulness={avg_faith:.2f}  "
          f"Relevance={avg_relev:.2f}  Recall={avg_recall:.2f}")
    print(f"  Overall:    {overall_avg:.2f}   Pass rate: {pass_rate:.0f}%  "
          f"(threshold ≥ {PASS_THRESHOLD})")
    print("=" * 65)
    print(f"\n  Full report: {output_path}\n")

    # Print failures with reasoning
    failures = [r for r in results if
                (r["scores"]["faithfulness"]["score"] +
                 r["scores"]["relevance"]["score"] +
                 r["scores"]["context_recall"]["score"]) / 3 < PASS_THRESHOLD]

    if failures:
        print(f"  ⚠ Failures ({len(failures)}):")
        for r in failures:
            print(f"\n  [{r['id']}] {r['question']}")
            print(f"    Answer: {r['answer'][:120]}...")
            print(f"    Faithfulness: {r['scores']['faithfulness']['reasoning']}")
            print(f"    Relevance:    {r['scores']['relevance']['reasoning']}")
            print(f"    Recall:       {r['scores']['context_recall']['reasoning']}")
    else:
        print("  All cases passed.")

    return output_path