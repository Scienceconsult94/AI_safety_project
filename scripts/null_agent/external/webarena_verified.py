"""Null-agent and refusal-agent floor of WebArena-Verified, scored offline by the package's own `eval-tasks` evaluator.

`write` creates one output folder per agent variant in the layout the evaluator reads
(<out>/<task_id>/agent_response.json + network.har, docs/getting_started/usage.md, Step 3) for all 812 tasks:
  null_emptytrace           agent_response.json is empty (no answer), network.har has zero entries
  null                      agent_response.json is empty (no answer), network.har holds only the start page load(s):
                            one GET per rendered start URL, status 200, text/html (what a harness records for an agent
                            that ends at once; the evaluator rejects a trace with zero entries)
  refusal_<type>_<STATUS>   agent_response.json = {"task_type": <type>, "status": <STATUS>, "retrieved_data": null,
                            "error_details": null}, start-page trace. One variant per task type (retrieve, mutate,
                            navigate) and per error status of the documented status list (fixed refusal agents).
  refusal_oracle            per task: the expected task type and, on tasks expecting an error status, that status,
                            otherwise NOT_FOUND_ERROR; start-page trace (upper bound for any refusal-only agent)
  claimdone_<type>          {"task_type": <type>, "status": "SUCCESS", "retrieved_data": null}, start-page trace
                            (supplementary: an agent that reports success at step 0 without acting)
It also writes a config with placeholder environment URLs (the evaluator only renders and de-renders URL strings; no site
is contacted). `eval-tasks` is then run by the caller with the benchmark's CLI.
`count` tabulates the unachievable tasks from the task files (Verified non-SUCCESS statuses; original WebArena "N/A").
`summarize` reads the evaluator's eval_results.json and per-task eval_result.json of every variant.

Usage (WebArena-Verified venv, isolated mode):
  python -I webarena_verified.py write --out-root <dir>
  webarena-verified eval-tasks --config <dir>/config.json --output-dir <dir>/<variant>
  python -I webarena_verified.py count --dataset <repo>/assets/dataset
  python -I webarena_verified.py summarize --out-root <dir> --out-csv <csv>
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

TYPES = ["retrieve", "mutate", "navigate"]
ERRORS = ["NOT_FOUND_ERROR", "ACTION_NOT_ALLOWED_ERROR", "PERMISSION_DENIED_ERROR", "DATA_VALIDATION_ERROR", "UNKNOWN_ERROR"]
EMPTY_HAR = {"log": {"version": "1.2", "creator": {"name": "null-agent", "version": "0"}, "pages": [], "entries": []}}
PLACEHOLDER_URLS = {
    "__SHOPPING__": "http://localhost:7770",
    "__SHOPPING_ADMIN__": "http://localhost:7780/admin",
    "__REDDIT__": "http://localhost:9999",
    "__GITLAB__": "http://localhost:8023",
    "__WIKIPEDIA__": "http://localhost:8888",
    "__MAP__": "http://localhost:3000",
}


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def resp(task_type: str, status: str) -> str:
    return json.dumps({"task_type": task_type, "status": status, "retrieved_data": None, "error_details": None})


def expected(task: dict) -> dict:
    return [e for e in task["eval"] if e["evaluator"] == "AgentResponseEvaluator"][0]["expected"]


def variants() -> list[tuple[str, object, str]]:
    """(name, response or callable(task) -> response, trace mode)"""
    out: list[tuple[str, object, str]] = [("null_emptytrace", "", "empty"), ("null", "", "start")]
    for t in TYPES:
        for s in ERRORS:
            out.append((f"refusal_{t}_{s}", resp(t, s), "start"))

    def oracle(task: dict) -> str:
        e = expected(task)
        return resp(e["task_type"], e["status"] if e["status"] != "SUCCESS" else "NOT_FOUND_ERROR")

    out.append(("refusal_oracle", oracle, "start"))
    for t in TYPES:
        out.append((f"claimdone_{t}", resp(t, "SUCCESS"), "start"))
    return out


def start_har(task: dict) -> dict:
    entries = []
    for u in task["start_urls"]:
        for k, v in PLACEHOLDER_URLS.items():
            u = u.replace(k, v)
        entries.append({
            "startedDateTime": "2026-01-01T00:00:00.000Z", "time": 1.0,
            "request": {"method": "GET", "url": u, "httpVersion": "HTTP/1.1", "cookies": [],
                        "headers": [{"name": "accept", "value": "text/html,application/xhtml+xml"},
                                    {"name": "sec-fetch-dest", "value": "document"},
                                    {"name": "sec-fetch-mode", "value": "navigate"}],
                        "queryString": [], "headersSize": -1, "bodySize": 0},
            "response": {"status": 200, "statusText": "OK", "httpVersion": "HTTP/1.1", "cookies": [],
                         "headers": [{"name": "content-type", "value": "text/html; charset=utf-8"}],
                         "content": {"size": 0, "mimeType": "text/html", "text": ""}, "redirectURL": "",
                         "headersSize": -1, "bodySize": 0},
            "cache": {}, "timings": {"send": 0, "wait": 1, "receive": 0},
        })
    return {"log": {"version": "1.2", "creator": {"name": "null-agent", "version": "0"}, "pages": [], "entries": entries}}


def write(out_root: Path, dataset: Path) -> None:
    tasks = json.loads((dataset / "webarena-verified.json").read_text(encoding="utf-8"))
    out_root.mkdir(parents=True, exist_ok=True)
    cfg = {"environments": {k: {"urls": [v]} for k, v in PLACEHOLDER_URLS.items()}}
    (out_root / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    for name, response, trace in variants():
        for t in tasks:
            d = out_root / name / str(t["task_id"])
            d.mkdir(parents=True, exist_ok=True)
            r = response(t) if callable(response) else response
            (d / "agent_response.json").write_text(r, encoding="utf-8")
            har = EMPTY_HAR if trace == "empty" else start_har(t)
            (d / "network.har").write_text(json.dumps(har), encoding="utf-8")
    print(f"wrote {len(variants())} variants x {len(tasks)} tasks under {out_root}")


def count(dataset: Path) -> None:
    v = json.loads((dataset / "webarena-verified.json").read_text(encoding="utf-8"))
    raw = json.loads((dataset / "test.raw.json").read_text(encoding="utf-8"))
    n = len(v)
    combos = Counter()
    no_net = Counter()
    for t in v:
        exp = [e for e in t["eval"] if e["evaluator"] == "AgentResponseEvaluator"][0]["expected"]
        if exp["status"] != "SUCCESS":
            has_net = any(e["evaluator"] == "NetworkEventEvaluator" for e in t["eval"])
            combos[(exp["task_type"], exp["status"], has_net)] += 1
            if not has_net:
                no_net[(exp["task_type"], exp["status"])] += 1
    k = sum(combos.values())
    print(f"Verified: {k}/{n} tasks expect a non-SUCCESS status ({100 * k / n:.1f}%)")
    for key, c in sorted(combos.items(), key=lambda x: -x[1]):
        print(f"   {c:3d} task_type={key[0]} status={key[1]} needs_network_event={key[2]}")
    k2 = sum(no_net.values())
    lo, hi = wilson(k2, n)
    print(f"Verified: {k2}/{n} = {100 * k2 / n:.1f}% [{100 * lo:.1f}-{100 * hi:.1f}] need only the status (no network event)")
    na = [t["task_id"] for t in raw if "N/A" in json.dumps(t["eval"].get("reference_answers") or {})]
    lo, hi = wilson(len(na), len(raw))
    print(f"Original test.raw.json: {len(na)}/{len(raw)} = {100 * len(na) / len(raw):.1f}% [{100 * lo:.1f}-{100 * hi:.1f}] "
          f"reference answer 'N/A' (ids {na})")


def summarize(out_root: Path, out_csv: Path | None) -> None:
    rows = []
    for name, _, _ in variants():
        vdir = out_root / name
        res = json.loads((vdir / "eval_results.json").read_text(encoding="utf-8"))
        passed, errors, statuses, n = [], [], Counter(), 0
        for td in sorted(vdir.iterdir(), key=lambda p: (len(p.name), p.name)):
            f = td / "eval_result.json"
            if not td.is_dir() or not f.exists():
                continue
            r = json.loads(f.read_text(encoding="utf-8"))
            n += 1
            statuses[r["status"]] += 1
            if r.get("score", 0) == 1.0:
                passed.append(int(td.name))
            if r["status"] == "error":
                errors.append(int(td.name))
        k = len(passed)
        lo, hi = wilson(k, n) if n else (float("nan"), float("nan"))
        summary = dict(res["summary"]["overall"])
        summary["version"] = res.get("webarena_verified_version")
        assert summary["success_count"] == len(passed) and summary["total"] == n, (name, summary, len(passed), n)
        print(f"{name:45s} pass {k}/{n} = {100 * k / max(n, 1):.2f}% [{100 * lo:.1f}-{100 * hi:.1f}] statuses {dict(statuses)} "
              f"evaluator summary {summary}")
        if k and k <= 60:
            print(f"   passed ids: {passed}")
        rows.append({"variant": name, "tasks_evaluated": n, "passed": k, "pass_pct": f"{100 * k / max(n, 1):.2f}",
                     "wilson_lo_pct": f"{100 * lo:.1f}", "wilson_hi_pct": f"{100 * hi:.1f}", "eval_errors": len(errors),
                     "passed_ids": " ".join(map(str, passed)), "evaluator_summary": json.dumps(summary)})
    if out_csv:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("--out-root", required=True, type=Path)
    w.add_argument("--dataset", required=True, type=Path)
    c = sub.add_parser("count")
    c.add_argument("--dataset", required=True, type=Path)
    s = sub.add_parser("summarize")
    s.add_argument("--out-root", required=True, type=Path)
    s.add_argument("--out-csv", type=Path)
    a = ap.parse_args()
    if a.cmd == "write":
        write(a.out_root, a.dataset)
    elif a.cmd == "count":
        count(a.dataset)
    else:
        summarize(a.out_root, a.out_csv)


if __name__ == "__main__":
    main()
