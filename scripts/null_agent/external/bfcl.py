"""Null-agent and refusal-agent floor of BFCL V4 (bfcl-eval), scored by the package's own evaluator.

Step 1 (`write`): writes result files for every scoring category (TEST_COLLECTION_MAPPING["all_scoring"]) into
<BFCL_PROJECT_ROOT>/result/<model>/<group>/BFCL_v4_<category>_result.json, the layout the evaluator reads (README:
"result/MODEL_NAME/BFCL_v3_TEST_CATEGORY_result.json"; grouped sub-folders as written by the generator). Entry IDs and
turn counts come from the package's own loaders (load_dataset_entry with include_prereq=False, the same call the
evaluator makes). Response per entry:
  single-turn (non-live, live, irrelevance, relevance)   result = <response>
  multi-turn                                              result = [[<response>] for each user turn]
  agentic (memory_*, web_search_*)                        result = [[<response>]]
with <response> = "" (null agent: empty reply, no function call) or a fixed refusal sentence (refusal agent).
The evaluator needs a registered model name to pick the decoder; the name only selects decode_ast / decode_execute.
OpenAI handler names need an API key at start-up, so a locally hosted name (Qwen/Qwen3-8B, Qwen/Qwen3-8B-FC) is used.
Step 2 (outside this script): `bfcl evaluate --model <model> --test-category all_scoring` with BFCL_PROJECT_ROOT set.
Step 3 (`summarize`): reads the evaluator's score files and data_overall.csv and recomputes the overall score from the
per-category accuracies with the formula of eval_runner_helper.generate_leaderboard_csv, as a cross-check.

Usage (BFCL venv, isolated + UTF-8 mode; BFCL_PROJECT_ROOT must be set because the package creates folders on import):
  set BFCL_PROJECT_ROOT=<work dir>
  <venv>/Scripts/python.exe -I -X utf8 bfcl.py write --model Qwen/Qwen3-8B --response ""
  <venv>/Scripts/python.exe -I -X utf8 bfcl.py summarize --model Qwen/Qwen3-8B --out-csv <csv> --label <variant>
"""

from __future__ import annotations

import argparse
import csv
import json
import os

from bfcl_eval.constants.category_mapping import TEST_COLLECTION_MAPPING
from bfcl_eval.constants.eval_config import RESULT_PATH, SCORE_PATH
from bfcl_eval.utils import (
    get_directory_structure_by_category,
    get_file_name_by_category,
    is_agentic,
    is_multi_turn,
    load_dataset_entry,
    load_ground_truth_entry,
)

CATS = TEST_COLLECTION_MAPPING["all_scoring"]
MULTI = ["multi_turn_base", "multi_turn_miss_func", "multi_turn_miss_param", "multi_turn_long_context"]
LIVE_AST = ["live_simple", "live_multiple", "live_parallel", "live_parallel_multiple"]


def write(model: str, response: str) -> None:
    mdir = RESULT_PATH / model.replace("/", "_")
    for cat in CATS:
        entries = load_dataset_entry(cat, include_prereq=False, include_language_specific_hint=False)
        gt = None
        if is_multi_turn(cat):
            gt = load_ground_truth_entry(cat)
            assert len(gt) == len(entries), (cat, len(gt), len(entries))
        out = []
        for k, e in enumerate(entries):
            if gt is not None:
                n_turns = len(e["question"])
                assert n_turns == len(gt[k]["ground_truth"]), (cat, e["id"], n_turns, len(gt[k]["ground_truth"]))
                res = [[response] for _ in range(n_turns)]
            elif is_agentic(cat):
                res = [[response]]
            else:
                res = response
            out.append({"id": e["id"], "result": res})
        d = mdir / get_directory_structure_by_category(cat)
        d.mkdir(parents=True, exist_ok=True)
        with open(d / get_file_name_by_category(cat, is_result_file=True), "w", encoding="utf-8") as f:
            for r in out:
                f.write(json.dumps(r) + "\n")
        print(f"{cat}: {len(out)} entries")


def summarize(model: str, out_csv: str | None, label: str) -> None:
    sdir = SCORE_PATH / model.replace("/", "_")
    acc = {}
    for p in sdir.rglob("BFCL_v4_*_score.json"):
        with open(p, encoding="utf-8") as f:
            head = json.loads(f.readline())
        cat = p.name[len("BFCL_v4_"):-len("_score.json")]
        acc[cat] = (head["accuracy"], head["correct_count"], head["total_count"])
    for cat in CATS:
        a = acc.get(cat)
        print(f"{cat:28s} " + ("missing" if a is None else f"{a[1]}/{a[2]} = {100 * a[0]:.2f}%"))

    def g(c):
        return acc[c][0]

    def n(c):
        return acc[c][2]

    simple = (g("simple_python") + g("simple_java") + g("simple_javascript")) / 3
    non_live = (simple + g("multiple") + g("parallel") + g("parallel_multiple")) / 4
    live = sum(g(c) * n(c) for c in LIVE_AST) / sum(n(c) for c in LIVE_AST)
    halluc = (g("irrelevance") + g("live_irrelevance")) / 2
    multi = sum(g(c) for c in MULTI) / 4
    web = (g("web_search_base") + g("web_search_no_snippet")) / 2
    mem = (g("memory_kv") + g("memory_vector") + g("memory_rec_sum")) / 3
    agentic = (web + mem) / 2
    overall = 0.10 * non_live + 0.10 * live + 0.10 * halluc + 0.30 * multi + 0.40 * agentic
    print(f"recomputed: non_live {100 * non_live:.2f} live {100 * live:.2f} irrelevance(hallucination) {100 * halluc:.2f} "
          f"multi_turn {100 * multi:.2f} agentic {100 * agentic:.2f} (web {100 * web:.2f}, memory {100 * mem:.2f}) "
          f"relevance {100 * g('live_relevance'):.2f} -> overall {100 * overall:.2f}")
    with open(SCORE_PATH / "data_overall.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    keep = ["Model", "Overall Acc", "Non-Live AST Acc", "Live Acc", "Multi Turn Acc", "Web Search Summary",
            "Memory Summary", "Relevance Detection", "Irrelevance Detection"]
    for r in rows:
        print("evaluator data_overall.csv:", {k: r[k] for k in keep if k in r})
    if out_csv:
        new = not os.path.exists(out_csv)
        with open(out_csv, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["variant", "decoder_model", "category", "correct", "total", "accuracy_pct"])
            for cat in CATS:
                a = acc[cat]
                w.writerow([label, model, cat, a[1], a[2], f"{100 * a[0]:.2f}"])
            ev = rows[0]["Overall Acc"].strip("%") if rows else "nan"
            for name, v in [("SUMMARY non_live", non_live), ("SUMMARY live", live),
                            ("SUMMARY irrelevance (hallucination)", halluc), ("SUMMARY multi_turn", multi),
                            ("SUMMARY agentic", agentic), ("SUMMARY overall (recomputed)", overall)]:
                w.writerow([label, model, name, "", "", f"{100 * v:.2f}"])
            w.writerow([label, model, "SUMMARY overall (evaluator data_overall.csv)", "", "", ev])


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("--model", required=True)
    w.add_argument("--response", required=True)
    s = sub.add_parser("summarize")
    s.add_argument("--model", required=True)
    s.add_argument("--out-csv")
    s.add_argument("--label", default="")
    a = ap.parse_args()
    if a.cmd == "write":
        write(a.model, a.response)
    else:
        summarize(a.model, a.out_csv, a.label)


if __name__ == "__main__":
    main()
