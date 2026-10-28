# Agent runs for the 30 airline tasks outside the block-1 sample (airline_full/PLAN.md, Q1), with the block-1 settings
# of run_sample20.ps1: (a) Pass^3 with Haiku agent + Haiku user, (b) the ground-truth agent (llm_agent_gt).
# Substring scorer, Anthropic models only. SPENDS MONEY (about $2, own estimate).
# Usage:  powershell -ExecutionPolicy Bypass -File .\scripts\runs\run_rest30.ps1 [-Part pass3|gt|both]
param([ValidateSet("pass3","gt","both")] [string]$Part = "both")
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = 1
$root  = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))  # repo root (this file lives in scripts\runs\)
$bench = Join-Path $root "tau2-bench"
$uv    = Join-Path $env:USERPROFILE ".local\bin\uv.exe"
if (-not (Test-Path (Join-Path $bench ".env")) -and -not (Test-Path (Join-Path $root ".env"))) {
    Write-Output "STOP: no .env found. No API call made."; exit 2
}
$sample = Get-Content (Join-Path $root "sample.json") -Raw -Encoding utf8 | ConvertFrom-Json
$ids = @($sample.population_ids | Where-Object { $sample.task_ids -notcontains $_ })
Write-Output ("task ids ({0}): {1}" -f $ids.Count, ($ids -join " "))
if ($ids.Count -ne 30) { Write-Output "STOP: expected 30 task ids. No API call made."; exit 2 }

Push-Location $bench
$common = @("--domain","airline","--task-split-name","base","--task-ids") + $ids + @(
    "--user","user_simulator","--user-llm","anthropic/claude-haiku-5-5",
    "--agent-llm-args","{}","--user-llm-args","{}",   # see run_pilot.ps1: default temperature 0.0 is rejected by current Anthropic models
    "--communicate-scorer","substring","--max-concurrency","3","--timeout","900","--seed","300")

if ($Part -eq "pass3" -or $Part -eq "both") {
    & $uv run --no-sync tau2 run-pass3 @common --agent llm_agent --agent-llm anthropic/claude-haiku-5-5 --save-to rest30_pass3_haiku
    & $uv run --no-sync python ..\scripts\summarize_run.py (Get-ChildItem data\simulations\rest30_pass3_haiku -Recurse -Filter results.json | Select-Object -ExpandProperty FullName)
}
if ($Part -eq "gt" -or $Part -eq "both") {
    & $uv run --no-sync tau2 run @common --num-trials 1 --agent llm_agent_gt --agent-llm anthropic/claude-haiku-5-5 --save-to rest30_gt_haiku
    & $uv run --no-sync python ..\scripts\summarize_run.py data\simulations\rest30_gt_haiku\results.json
}
Pop-Location
Write-Output "done -> copy the results.json files to results\runs\, append cost.md, run scripts\agent_rows.py --ids rest"
