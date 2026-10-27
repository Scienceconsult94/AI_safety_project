# Agent runs for the 20 sampled tasks (sample.json): (a) Pass^3 with Haiku agent + Haiku user,
# (b) solvability check with the ground-truth agent (llm_agent_gt). Substring scorer, Anthropic models only.
# Preconditions: as in run_pilot.ps1; pilot completed; cost.md cumulative + estimate < $30.
# Usage:  powershell -ExecutionPolicy Bypass -File .\scripts\runs\run_sample20.ps1 [-Part pass3|gt|both]
param([ValidateSet("pass3","gt","both")] [string]$Part = "both")
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = 1
$root  = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))  # repo root (this file lives in scripts\runs\)
$bench = Join-Path $root "tau2-bench"
$uv    = Join-Path $env:USERPROFILE ".local\bin\uv.exe"
if (-not (Test-Path (Join-Path $bench ".env")) -and -not (Test-Path (Join-Path $root ".env"))) {
    Write-Output "STOP: no .env found. No API call made."; exit 2
}
$ids = (Get-Content (Join-Path $root "sample.json") -Raw -Encoding utf8 | ConvertFrom-Json).task_ids
Write-Output ("task ids ({0}): {1}" -f $ids.Count, ($ids -join " "))

Push-Location $bench
# The NL-assertion judge is not invoked by `tau2 run` at v2.0.0 (EvaluationType.ALL default, src/tau2/runner/batch.py); patches/ stays unapplied.

$common = @("--domain","airline","--task-split-name","base","--task-ids") + $ids + @(
    "--user","user_simulator","--user-llm","anthropic/claude-haiku-5-5",
    "--agent-llm-args","{}","--user-llm-args","{}",   # see run_pilot.ps1: default temperature 0.0 is rejected by current Anthropic models
    "--communicate-scorer","substring","--max-concurrency","3","--timeout","900","--seed","300")

if ($Part -eq "pass3" -or $Part -eq "both") {
    & $uv run --no-sync tau2 run-pass3 @common --agent llm_agent --agent-llm anthropic/claude-haiku-5-5 --save-to sample20_pass3_haiku
    & $uv run --no-sync python ..\scripts\summarize_run.py (Get-ChildItem data\simulations\sample20_pass3_haiku -Recurse -Filter results.json | Select-Object -ExpandProperty FullName)
}
if ($Part -eq "gt" -or $Part -eq "both") {
    & $uv run --no-sync tau2 run @common --num-trials 1 --agent llm_agent_gt --agent-llm anthropic/claude-haiku-5-5 --save-to sample20_gt_haiku
    & $uv run --no-sync python ..\scripts\summarize_run.py data\simulations\sample20_gt_haiku\results.json
}
Pop-Location
Write-Output "done -> reconcile cost with the Anthropic Console, append cost.md, fill haiku_pass in audit_log.csv"
