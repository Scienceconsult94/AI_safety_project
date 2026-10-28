# Strong-vs-weak check on the 20 sampled airline tasks (sample.json): Pass^3 with a Sonnet agent and the same Haiku user
# simulator, same scorer and settings as scripts\runs\run_sample20.ps1. Question: does the exam separate a stronger model from
# claude-haiku-5-5 (results\runs\sample20_pass3_haiku), and does the separation survive the v2 re-scoring (scripts\v2\rescore.py)?
# Spends money (own estimate before the run: about $8 for 60 simulations; Sonnet input/output prices are 30x Haiku's).
# Preconditions: as in run_sample20.ps1; cost.md cumulative + estimate < $30; this file is NOT run by any other script.
# Usage:  powershell -ExecutionPolicy Bypass -File .\scripts\runs\run_sonnet20.ps1 [-DryRun]
param([switch]$DryRun)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = 1
$root  = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
$bench = Join-Path $root "tau2-bench"
$uv    = Join-Path $env:USERPROFILE ".local\bin\uv.exe"
if (-not (Test-Path (Join-Path $bench ".env")) -and -not (Test-Path (Join-Path $root ".env"))) {
    Write-Output "STOP: no .env found. No API call made."; exit 2
}
$ids = (Get-Content (Join-Path $root "sample.json") -Raw -Encoding utf8 | ConvertFrom-Json).task_ids
Write-Output ("task ids ({0}): {1}" -f $ids.Count, ($ids -join " "))

$common = @("--domain","airline","--task-split-name","base","--task-ids") + $ids + @(
    "--user","user_simulator","--user-llm","anthropic/claude-haiku-5-5",
    "--agent-llm-args","{}","--user-llm-args","{}",
    "--communicate-scorer","substring","--max-concurrency","3","--timeout","900","--seed","300")
$cmd = @("run","--no-sync","tau2","run-pass3") + $common + @("--agent","llm_agent","--agent-llm","anthropic/claude-sonnet-5-5","--save-to","sample20_pass3_sonnet")
if ($DryRun) { Write-Output ("DRY RUN, no API call: uv " + ($cmd -join " ")); exit 0 }

Push-Location $bench
& $uv @cmd
& $uv run --no-sync python ..\scripts\summarize_run.py (Get-ChildItem data\simulations\sample20_pass3_sonnet -Recurse -Filter results.json | Select-Object -ExpandProperty FullName)
Pop-Location
Write-Output "done -> copy results.json to results\runs\sample20_pass3_sonnet.results.json, append cost.md, then re-score with scripts\v2\rescore.py"
