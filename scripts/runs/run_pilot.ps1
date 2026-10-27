# Pilot: 5 airline tasks end-to-end on Claude Haiku 5.5 (agent and user), substring scorer.
# Preconditions: tau2-bench\.env with ANTHROPIC_API_KEY exists (created by hand; never read or printed here);
#                spending limit set in the Anthropic Console; cost.md cumulative < $30.
# Usage:  powershell -ExecutionPolicy Bypass -File .\scripts\runs\run_pilot.ps1
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = 1
$root  = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))  # repo root (this file lives in scripts\runs\)
$bench = Join-Path $root "tau2-bench"
$uv    = Join-Path $env:USERPROFILE ".local\bin\uv.exe"

if (-not (Test-Path (Join-Path $bench ".env")) -and -not (Test-Path (Join-Path $root ".env"))) {
    Write-Output "STOP: no .env found (tau2-bench\.env or ==Project\.env). No API call made."; exit 2
}
Push-Location $bench
# The NL-assertion judge is not invoked by `tau2 run` at v2.0.0 (EvaluationType.ALL default, src/tau2/runner/batch.py); patches/ stays unapplied.
# --agent-llm-args '{}' --user-llm-args '{}': tau2 defaults both to {"temperature": 0.0} (src/tau2/config.py:28-31);
# current Anthropic models reject a non-default temperature with HTTP 400, which tau2 counts as an infra error
# (first pilot attempt 2026-10-27: 5/5 infra errors, $0). Empty args = provider defaults; no code patched.

& $uv run --no-sync tau2 run `
    --domain airline --task-split-name base --num-tasks 5 --num-trials 1 `
    --agent llm_agent --agent-llm anthropic/claude-haiku-5-5 `
    --user user_simulator --user-llm anthropic/claude-haiku-5-5 `
    --agent-llm-args '{}' --user-llm-args '{}' `
    --communicate-scorer substring `
    --max-concurrency 3 --timeout 900 --seed 300 `
    --save-to pilot_5_haiku
$code = $LASTEXITCODE
& $uv run --no-sync python ..\scripts\summarize_run.py data\simulations\pilot_5_haiku\results.json
Pop-Location
Write-Output "tau2 exit code: $code  -> now reconcile cost with the Anthropic Console and append a row to cost.md"
exit $code
