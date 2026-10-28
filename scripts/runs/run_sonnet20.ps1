# Strong-vs-weak check on the 20 sampled airline tasks (sample.json): a Sonnet agent with the same Haiku user simulator,
# same scorer and settings as scripts\runs\run_sample20.ps1. Question: does the exam separate a stronger model from
# claude-haiku-5-5 (results\runs\sample20_pass3_haiku), and does the separation survive the v2 re-scoring (scripts\v2\rescore.py)?
# Spends money. Own estimate from the token counts of the Haiku run on the same 20 tasks x 3 trials (agent: 7.14M input and
# 0.30M output tokens; no prompt above 25K tokens): at Sonnet 5.5 prices ($2 / $10 per MTok, 20x Haiku 5.5) about $17.4 for
# 3 trials with the same output volume, about $20-23 if Sonnet's thinking doubles or triples the output; -Trials 1 costs
# about a third of that. The user simulator (Haiku) adds about $0.15 for 3 trials.
# Preconditions: as in run_sample20.ps1; cost.md cumulative + estimate < the hard stop; this file is NOT run by any other script.
# Usage:  powershell -ExecutionPolicy Bypass -File .\scripts\runs\run_sonnet20.ps1 [-Trials 1|2|3] [-DryRun]
param([switch]$DryRun, [ValidateSet(1, 2, 3)] [int]$Trials = 3)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = 1
$root  = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
$bench = Join-Path $root "tau2-bench"
$uv    = Join-Path $env:USERPROFILE ".local\bin\uv.exe"
if (-not (Test-Path (Join-Path $bench ".env")) -and -not (Test-Path (Join-Path $root ".env"))) {
    Write-Output "STOP: no .env found. No API call made."; exit 2
}
$ids = (Get-Content (Join-Path $root "sample.json") -Raw -Encoding utf8 | ConvertFrom-Json).task_ids
Write-Output ("task ids ({0}): {1}; trials: {2}" -f $ids.Count, ($ids -join " "), $Trials)

$common = @("--domain","airline","--task-split-name","base","--task-ids") + $ids + @(
    "--user","user_simulator","--user-llm","anthropic/claude-haiku-5-5",
    "--agent-llm-args","{}","--user-llm-args","{}",
    "--communicate-scorer","substring","--max-concurrency","3","--timeout","900","--seed","300")
$name = "sample20_sonnet_t$Trials"
if ($Trials -eq 3) { $sub = @("run","--no-sync","tau2","run-pass3") } else { $sub = @("run","--no-sync","tau2","run","--num-trials","$Trials") }
$cmd = $sub + $common + @("--agent","llm_agent","--agent-llm","anthropic/claude-sonnet-5-5","--save-to",$name)
if ($DryRun) { Write-Output ("DRY RUN, no API call: uv " + ($cmd -join " ")); exit 0 }

Push-Location $bench
& $uv @cmd
& $uv run --no-sync python ..\scripts\summarize_run.py (Get-ChildItem "data\simulations\$name" -Recurse -Filter results.json | Select-Object -ExpandProperty FullName)
Pop-Location
Write-Output "done -> copy results.json to results\runs\$name.results.json, append cost.md, then re-score with scripts\v2\rescore.py"
