"""Fill the human-label sheet one answer at a time, in the terminal.

Shows the question, the reference answer and the answer to grade, with no arm and no grader
verdict, and asks for 1 (correct) or 0 (incorrect). The sheet is saved after every label, so the
session can be stopped and resumed. Rows that already have a label are skipped.

Use the same rule the LLM judge was given: correct only if the final conclusion states the same
fact as the reference; wrong, missing, hedged between a right and a wrong value, or inventing
something the reference says is not recorded counts as incorrect.

The sheet is already in a seeded random order (judge.py), so --first N labels a fixed random
sample of N runs instead of the whole sheet.

Usage: python label.py --label v2-api [--first 100]
Keys:  1 correct, 0 incorrect, s skip for now, b go back one, q save and quit
"""
import argparse, csv, sys, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ["id", "question", "reference", "answer", "hand"]


def save(sheet, rows):
    with sheet.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def wrap(text, width=100):
    return "\n".join(textwrap.fill(line, width) if line.strip() else "" for line in text.splitlines())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--first", type=int, default=None, help="label only the first N rows of the shuffled sheet")
    a = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    sheet = ROOT / "results" / a.label / "hand_labels.csv"
    with sheet.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    scope = rows[:a.first] if a.first else rows
    todo = [i for i, r in enumerate(scope) if r.get("hand", "").strip() not in ("0", "1")]
    print(f"{len(scope) - len(todo)} of {len(scope)} already labelled.")
    pos = 0
    while 0 <= pos < len(todo):
        r = rows[todo[pos]]
        print("\n" + "=" * 100)
        print(f"[{pos + 1} of {len(todo)} left]  id {r['id']}")
        print(f"\nQUESTION:  {r['question']}")
        print(f"\nREFERENCE: {wrap(r['reference'])}")
        print(f"\nANSWER:\n{wrap(r['answer']) or '(empty)'}")
        k = input("\n1 correct / 0 incorrect / s skip / b back / q quit > ").strip().lower()
        if k in ("0", "1"):
            r["hand"] = k
            save(sheet, rows)
            pos += 1
        elif k == "s":
            pos += 1
        elif k == "b":
            pos = max(0, pos - 1)
        elif k == "q":
            break
    save(sheet, rows)
    left = sum(1 for r in scope if r.get("hand", "").strip() not in ("0", "1"))
    print(f"\nSaved. {len(scope) - left} of {len(scope)} labelled, {left} left.")


if __name__ == "__main__":
    sys.exit(main())
