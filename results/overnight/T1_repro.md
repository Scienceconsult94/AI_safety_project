# T1: does a fresh clone reproduce the published numbers?

Date: 2026-10-31, 18:07 to 18:53 local time. Done on this machine, in a folder separate from the project: `<fresh-folder>\`.
No model or API call was made. No `.env` file was read. In every rebuild runner, the assistant-specific API variables were removed from the environment. No `.env` exists in any folder from the clone up to the drive root; this was checked with `Test-Path` only. Nothing in the project folder or its `tau2-bench` was run or changed. The project folder was used for one write, this file, and for one read-only package-version query of the system Python 3.11 (not in the project folder).

**Verdict: REPRODUCES WITH DOC FIXES**

## 1. Environment

| item | value |
|---|---|
| repository clone | `https://github.com/Scienceconsult94/AI_safety_project` -> `<fresh-folder>\AI_safety_project`, commit `a3fd7e18648fc88d060ea731099bad0da2be8cfc` (= a3fd7e1, as expected) |
| tau2-bench | cloned into the clone as `tau2-bench/`, checked out `989d3285ae669e49503324bdb9981bf14fccedeb` (`HEAD, tag: v2.0.0`) |
| uv | `<user-home>\.local\bin\uv.exe`, uv 0.13.6 (329bf9448 2026-10-26); this is the same file as the `$uv` path written in STRUCTURE.md |
| tau2 venv | `tau2-bench/.venv`, CPython 3.12.16. uv found a uv-managed 3.12.16 that was already on the machine and did not download one. `UV_CACHE_DIR` was pointed at `<fresh-folder>\uv_cache`, so all 77 packages were downloaded fresh from the lock file. |
| analysis venv | `<fresh-folder>\py311`, made with `py -3.11 -m venv` (CPython 3.11.2), then `pip install pandas matplotlib statsmodels jupyter` (pip cache in `<fresh-folder>\pip_cache`) |
| package versions installed | pandas 3.1.0, matplotlib 3.11.2, statsmodels 0.15.0, numpy 2.4.6, scipy 1.17.1, jupyter 1.1.1, nbconvert 7.17.2 |
| author's system Python 3.11, for comparison (read-only query) | pandas 2.3.0, matplotlib 3.10.3, statsmodels 0.14.4, numpy 2.1.0, nbconvert 7.16.4. The repository does not pin these versions. |
| `python` on PATH | a Python 3.14.3 on PATH. It has no pandas, statsmodels or matplotlib. For the `python ...` lines, the runner put `<fresh-folder>\py311\Scripts` first on PATH. |
| shells | DEMO in Git Bash, as DEMO.md prints it; the STRUCTURE blocks in Windows PowerShell 5.1, as printed |
| git | 2.50.1.windows.1 |

Runner scripts are in `<fresh-folder>\runner\`. Each one runs the documented lines in order, in one PowerShell session, and logs the exit code and time of every line.

## 2. Steps and times

| step | command(s) | outcome | time |
|---|---|---|---|
| clone repo | `git clone https://github.com/Scienceconsult94/AI_safety_project` | ok, a3fd7e1 | 2 s |
| Setup | `git clone https://github.com/sierra-research/tau2-bench`; `cd tau2-bench`; `git checkout 989d3285...` | ok | 52 s |
| Setup | `uv sync` | ok: "Resolved 186 packages", "Installed 77 packages"; log `<fresh-folder>\logs\uv_sync.log` | 11.5 s |
| Setup | `py -3.11 -m venv ...\py311`; `pip install pandas matplotlib statsmodels jupyter` | ok; log `<fresh-folder>\logs\pip_install.log` | 123 s |
| DEMO | `cd tau2-bench`; `PYTHONUTF8=1 uv run --no-sync python ../scripts/demo/demo.py` | exit 0, "(done in 13 s ...)"; log `<fresh-folder>\logs\demo_full.log` | 13 s |
| DEMO | the same with `--only 1` .. `--only 4` | all exit 0; logs `...\logs\demo_only{1..4}.log` | 12 s, 0 s, 0 s, 0 s |
| Rebuild A | both STRUCTURE.md sequences exactly as printed (section 4) | 19 of 20 lines exit 0; `build_audit_log.py` exits 1 | 33.0 min in total (block 1: 100 s; block 2: 31.3 min) |
| Rebuild B | after `git checkout -- .`, the block-1 sequence again with the copy step added (section 6, fix 1) | all 11 lines exit 0 | 2.0 min |

## 3. DEMO comparison

The demo output was compared line by line with the "Expected output of `demo.py`, shortened" block in DEMO.md (25 lines, 22 of them non-empty).
- 17 of the 22 expected non-empty lines appear **exactly** in the actual output, in the same order. These include `full reward on 23 of 50 tasks: 0, 1, 2, 4, 5, 6, 9, 10, 13, 26, 27, 28, 31, 34, 36, 38, 41, 43, 45, 46, 47, 48, 49`, both task-72 orders with `final database identical: True`, `3 of 4 items carry another variant's price and options.`, and the four task-105 lines (21.10; 17.00; rejection message; `True`; the assertion).
- The other 5 lines are the header and the four rows of the task-20 table. The actual output has one extra column, `stored options`, which holds `{'skin tone': 'medium', 'kit size': 'professional', 'brand': 'Brand A'}` on every row. With that column removed, all 5 lines match the expected text character for character. This is the "shortened" form the document announces, not a difference in content.
- The explanation lines of the actual output are not in the expected block. That is also by design ("shortened").
- Differences in numbers or verdicts: **none**. Run time: 13 s (DEMO.md: "under a minute", "19 and 37 seconds").

## 4. Rebuild A: both sequences exactly as printed

Per-line logs are in `<fresh-folder>\logs\rebuild_A\NN.log` (UTF-16). The step table is `...\logs\rebuild_A\steps.tsv`.

| # | line | exit | time |
|---|---|---|---|
| 01 | `& $uv run --no-sync python ..\scripts\static_scan.py` | 0 | 53.7 s |
| 02 | `... probe_2h.py` | 0 | 18.7 s |
| 03 | `... extract_tasks.py` | 0 | 0.3 s |
| 04 | `... agent_rows.py --log ..\results\runs\sample20.log` | 0, but **found no simulations** (see below) | 0.3 s |
| 05 | `... probe_32.py --dry` | 0 | 9.9 s |
| 06 | `python -I scripts\build_audit_log.py` | **1**: validator `ERR line N: haiku_pass '' must be k/n for agent_run`, 118 rows | 0.5 s |
| 07 | `python -I scripts\rereview_agreement.py` | 0 (27/29, kappa 0.758; 29/29) | 0.1 s |
| 08 | `python -I scripts\make_summary.py --selftest` | 0 ("selftest passed") | 7.5 s |
| 09 | `python -I scripts\make_summary.py` | 0 | 2.1 s |
| 10 | `python -m jupyter nbconvert --to notebook --execute --inplace analysis.ipynb` | 0 | 6.4 s |
| 11 | `python -I scripts\v2\make_tasks_v2.py --check` | 0 ("tasks_airline_v2.json is up to date") | 0.1 s |
| 12 | `& $uv run ... v2\scorer_v2.py --selftest` | 0 | 11.3 s |
| 13 | `... v2\noop_scan_v2.py` | 0 | 65.5 s |
| 14 | `... v2\rescore.py --no-judge` | 0 | 237.8 s |
| 15 | `... v2\rescore.py` | 0; replay gate 76/76; "Judge calls this run: 0" (all 88 pairs from cache) | 452.6 s |
| 16 | `... v2\rescore.py --set fresh` | 0; judge calls 0 | 660.9 s |
| 17 | `... v2\rescore.py --set sonnet` | 0; replay gate 60/60; judge calls 0 | 428.6 s |
| 18 | `... v2\judge_handcheck.py --build` | 0 (46 items) | 8.3 s |
| 19 | `... v2\judge_reparse_check.py` | 0 (610 replies, 53 arrays, 32 recovered, 0 verdicts changed) | 8.7 s |
| 20 | `python -I -X utf8 scripts\v2\make_summary_v2.py` | 0 | 6.3 s |

**Why line 04 finds nothing.** `scripts/agent_rows.py` reads `tau2-bench/data/simulations/<run>/**/results.json`. A fresh tau2-bench clone has no `data/simulations/` folder. STRUCTURE.md line 179 says only that "the same files are kept in `results/runs/`". It does not say they must be copied back. So the script finds 0 simulations, exits 0, and overwrites committed files with empty ones:
- `results/haiku_pass.csv`: `haiku_pass` emptied on 40 rows, 5 defect rows set from 1 to 0;
- `results/agent_runs_summary.md`: every run column is `-`;
- `results/agent_triage.md`: "none: every evaluated trajectory succeeded".

`build_audit_log.py` then writes an `audit_log.csv` in which 118 rows have an empty `haiku_pass` and changed `evidence`, `note` and `date`, and the validator fails (exit 1). `summary_numbers.md` stays byte-identical even so: Table 4 is read from `results/runs/*.results.json`, and the defect rows come from the review files read last.

`git status --short` after rebuild A showed 18 modified files and no untracked file. Saved in `...\logs\rebuild_A_status.txt`, `rebuild_A_diffstat.txt`, `rebuild_A_full.diff`. Per-file analysis: `...\logs\compare_A.txt`.

| file | what differs | class |
|---|---|---|
| `results/haiku_pass.csv`, `results/agent_runs_summary.md`, `results/agent_triage.md`, `audit_log.csv` | emptied agent-run rows, as described above | (c) caused by the missing copy step. Gone in rebuild B. |
| `results/static_scan.csv` | only the `scan_date` column (2026-10-28 -> 2026-10-31) | (b) |
| `results/probe_32/setup.json` | only `created_utc` (documented in STRUCTURE.md as "rewrites ... (timestamp)") | (b) |
| `results/v2/rescore.csv`, `rescore_fresh.csv`, `rescore_sonnet.csv` | only the `overlay_commit` column (5f4d92a / d55bd49 / c470f5a -> a3fd7e1); every reward and verdict column is identical | (b) |
| `results/v2/provenance.json`, `provenance_fresh.json`, `provenance_sonnet.json` | `overlay_commit`; `judge_cost` calls, retries and tokens -> 0 (the cache was replayed) | (b), as STRUCTURE.md's "Rebuild check" note describes |
| `results/v2/rescore_summary.md`, `_fresh.md`, `_sonnet.md` | the provenance line, the "Judge calls this run" line, and the section "Judge as an instrument (this run's calls only ...)", which is left out when there are 0 calls. The pass-count tables and the flip tables are identical. | (b) run metadata |
| `block2/summary_v2.md` | 1 line: "overlay commit 5f4d92a" -> "a3fd7e1" in the provenance sentence; every number is identical | (b) |
| `fig_defects.png` | the bytes differ. Viewed side by side, the bars, whiskers and labels are the same (1/20, 11/20, 0/20, 4/20, 8/20, 0/20, 23/50); only the font rendering differs (matplotlib 3.11.2 here, 3.10.3 in the committed PNG metadata) | (b) rendering only |
| `analysis.ipynb` | execution timestamps; the embedded PNG (same rendering difference); and the **text output of cell 3** (see section 7) | (b) for timestamps and PNG; (a) for cell 3, where the committed output is stale |

## 5. Rebuild B: the block-1 sequence with the copy step

Before rebuild B, `git checkout -- .` restored the clone. STRUCTURE.md was then corrected in the clone (section 6, fixes 1 and 2), and the block-1 sequence was run again with the copy line. Block 2 was not run again: in rebuild A it showed only stamp differences, and none of its outputs depends on the agent-run files. Logs: `<fresh-folder>\logs\rebuild_B\`. Comparison: `...\logs\compare_B.txt`. Status and diffs: `rebuild_B_status.txt`, `rebuild_B_diffstat.txt`, `rebuild_B_text.diff`.

- All 11 lines exit 0. `build_audit_log.py`: "audit_log.csv: 503 rows, 0 errors"; "defective tasks without the no-op class (2a, 2b): 16/20; counting it: 18/20".
- **Byte-identical to the commit:** `audit_log.csv`, `results/haiku_pass.csv`, `results/agent_runs_summary.md`, `results/agent_triage.md`, `results/trajectories/*`, `results/task_cards/*`, `results/probe_2h.csv`, `results/rereview.csv`, `results/rereview_summary.md`, `summary_numbers.md`.
- `git status --short` after rebuild B:

```
 M STRUCTURE.md                  <- the doc correction applied in the clone (section 6)
 M analysis.ipynb                <- timestamps + PNG rendering (b); cell-3 output: committed copy is stale (section 7)
 M fig_defects.png               <- font rendering only (b)
 M results/probe_32/setup.json   <- created_utc only (b)
 M results/static_scan.csv       <- scan_date only (b)
```

**Headline numbers against README.md and summary_numbers.md.** The output of `make_summary.py` is identical to the committed `summary_numbers.md`. The re-executed notebook's cell-3 output is equal to it character for character. Checked against the README Block 1 table: 16/20 = 0.80 [0.58, 0.92] and 18/20; static and probes 12/20; no-op 23/50 = 0.46; tasks passed 3/3 12/20 = 0.60; ground-truth agent 11/16; blind re-review 27/29, kappa 0.76 (0.758); scoring validity 11/20; determinism 8/20; without 2g 15/20. All match.

Block 2 (`block2/summary_v2.md` and `results/v2/rescore_summary*.md` rebuilt; numbers identical) against the README:
- H1: 23/50 -> 0/50; refusal bot 14/23.
- H2: 24/78 -> 4/78.
- H3: 2 flips of 76 (task 9 t0 pass->fail through nl_enforce; task 7 t0 fail->pass through the criteria text).
- H4: task 7 4/4, task 44 3/4, task 32 1/4.
- H5: tasks passed 3/3 0.60 -> 0.60; pass^1 0.73 -> 0.78.
- Sonnet re-score: v1 51/60 = 0.850, V2 53/60 = 0.883, tasks passed 3/3 16/20.

All match.

Not run here, because they are outside the two requested sequences: the retail sequence, the strong-vs-weak `compare.py`, `tau2_null_agent.py` and the whole-airline-domain sequence. Their numbers (retail 61/114 and 38/114; p = 0.125 and 0.039; the null-agent floors; 34/50) were not re-derived in this check.

## 6. Documentation fixes needed

Line numbers are those of `STRUCTURE.md` at a3fd7e1. Fixes 1 and 2 were applied in the clone and tested. Fixes 3 and 4 are the same defects in sequences that were not run.

**Fix 1 (required: without it the literal sequence corrupts committed outputs and the validator fails).** STRUCTURE.md, block "Rebuild everything (offline, no API calls)", insert before line 169.
- old (line 169): `& $uv run --no-sync python ..\scripts\agent_rows.py --log ..\results\runs\sample20.log`
- new (two lines):
  `foreach ($r in "sample20_pass3_haiku", "sample20_gt_haiku") { New-Item -ItemType Directory -Force data\simulations\$r | Out-Null; Copy-Item ..\results\runs\$r.results.json data\simulations\$r\results.json }   # agent_rows.py reads the recorded runs from here`
  `& $uv run --no-sync python ..\scripts\agent_rows.py --log ..\results\runs\sample20.log`

With this change the agent-run outputs, `audit_log.csv` and the trajectories are byte-identical to the commit. The committed outputs cite `tau2-bench/data/simulations/<run>/results.json`, which confirms this folder layout. As an option, line 179 could say: "a fresh clone has no `tau2-bench/data/simulations/`; the copy line above restores the runs from `results/runs/`."

**Fix 2 (required to run the Block 2 block on its own).** STRUCTURE.md line 186, block "Block 2 rebuild (offline parts)".
- old: `cd tau2-bench; $env:PYTHONUTF8 = 1`
- new: `cd tau2-bench; $env:PYTHONUTF8 = 1; $uv = "$env:USERPROFILE\.local\bin\uv.exe"`

`$uv` is defined only in the first block. In a new PowerShell session, `& $uv run ...` fails with "The expression after '&' in a pipeline element produced an object that was not valid" (tested). The block works only when it runs in the same session right after the first block, which is how rebuild A ran it.

**Fix 3 (same defect as fix 2; not exercised).** STRUCTURE.md lines 208 (Retail block) and 233 (Strong vs weak block): the same old text, and the same new text as fix 2.

**Fix 4 (same defect as fix 1; not exercised).** STRUCTURE.md line 268 (whole airline domain): `python -I scripts\agent_rows.py --ids rest` needs `results/runs/rest30_pass3_haiku.results.json` and `rest30_gt_haiku.results.json` copied to `tau2-bench\data\simulations\rest30_pass3_haiku\results.json` and `...\rest30_gt_haiku\results.json` first. Line 268 runs from the repository root, so it needs a copy line with `tau2-bench\data\simulations\...` paths.

**Suggested clarifications (not needed to make anything run).**
- STRUCTURE.md line 156 and the "Rebuild everything" intro: say that `python` in the PowerShell blocks must be the Python 3.11 environment, for example "activate it first: `<venv>\Scripts\Activate.ps1`". Here, `python` on PATH is 3.14 without pandas, statsmodels or matplotlib, so the literal `python -I ...` lines would fail without activation.
- `$uv = "$env:USERPROFILE\.local\bin\uv.exe"` assumes uv's standalone installer. `$uv = (Get-Command uv).Source` would also work for pip, winget or scoop installs.
- The analysis packages are not pinned. Today's pip versions (pandas 3.1.0, matplotlib 3.11.2, statsmodels 0.15.0) reproduced every number. The only effect was the PNG font rendering.
- `scripts/agent_rows.py` exits 0 and writes empty outputs when it finds no simulations. A hard stop on 0 loaded simulations would turn the silent corruption into a clear error. This is a code suggestion, not a doc fix.

## 7. Mismatches

The headline numbers (README.md, summary_numbers.md, block2/summary_v2.md, results/v2/rescore_summary*.md) have **no mismatches**: every number checked reproduced exactly.

One committed file shows numbers that do not match the rebuild: **`analysis.ipynb`, the stored output of cell 3**. It was executed on 2026-10-27T21:23:57Z and is older than the current `summary_numbers.md`. Re-executing it, as STRUCTURE.md prescribes, gives output equal to `summary_numbers.md`. The diff is in `<fresh-folder>\logs\analysis_ipynb_HEAD_vs_summary.diff`, and the stale text in `...\logs\analysis_ipynb_HEAD_cell3_output.md`.

| row in the notebook's Table 1 / 2 / 2b | published (committed notebook output) | reproduced (= summary_numbers.md = README) |
|---|---|---|
| defective tasks, sampled tasks (headline row) | 18/20 = 0.900 [0.699, 0.972] (old definition, no-op class included) | 16/20 = 0.800 [0.584, 0.919] (no-op class on its own line); 18/20 appears as a separate "counting the no-op class" row |
| static and probe checks only | 13/20 = 0.650 [0.433, 0.819] | 12/20 = 0.600 [0.387, 0.781] |
| tasks whose only confirmed defects come from agent_run checks | 5/20 = 0.250 [0.112, 0.469] | 4/20 = 0.200 [0.081, 0.416] |
| Table 2, 2 Scoring validity | 12/20 = 0.600 [0.387, 0.781] | 11/20 = 0.550 [0.342, 0.742] |
| Table 2b, check 2h | 3 rows, 3/20 | 4 rows, 4/20 |
| rows missing from the committed output | "counting the no-op class, static and probe checks only 14/20"; "also excluding check 2g 15/20" | present |

Fix: commit the re-executed `analysis.ipynb`. Anyone opening the notebook on GitHub currently sees 18/20 and 13/20 next to a README that says 16/20 and 12/20.

## 8. Verdict

REPRODUCES WITH DOC FIXES. The demo matches its expected output, and both offline rebuild sequences reproduce every published number. Two documentation fixes are needed: a copy step before `agent_rows.py`, and `$uv` defined in the Block 2 block. Without the first, the literal sequence silently overwrites `results/haiku_pass.csv`, `agent_runs_summary.md`, `agent_triage.md` and `audit_log.csv` with empty agent-run rows, and the validator fails. Separately, the committed `analysis.ipynb` output is stale (section 7).
