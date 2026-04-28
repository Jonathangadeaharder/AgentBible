#!/usr/bin/env pwsh
# Install commit message validation as a git hook

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$hookDir = Join-Path $scriptDir ".git\hooks"
$hookFile = Join-Path $hookDir "commit-msg"
$validatorScript = Join-Path $scriptDir "validate-commits.ps1"

# Check if we're in a git repository
if (-not (Test-Path (Join-Path $scriptDir ".git"))) {
    Write-Host "Error: Not in a git repository" -ForegroundColor Red
    exit 1
}

# Ensure hooks directory exists
if (-not (Test-Path $hookDir)) {
    New-Item -ItemType Directory -Path $hookDir -Force | Out-Null
}

# Create the hook file
$hookContent = @"
#!/bin/sh
# Git commit-msg hook - validates commit messages

SCRIPT_DIR="`$(cd "`$(dirname "`$0")/../.." && pwd)"
VALIDATOR_SCRIPT="`$SCRIPT_DIR/validate-commits.ps1"
COMMIT_MSG_FILE="`$1"

if [ -f "`$VALIDATOR_SCRIPT" ]; then
    pwsh -File "`$VALIDATOR_SCRIPT" -Hook -CommitMsgFile "`$COMMIT_MSG_FILE"
    exit `$?
else
    echo "Warning: Commit validator not found at `$VALIDATOR_SCRIPT"
    exit 0
fi
"@

Set-Content -Path $hookFile -Value $hookContent -Encoding UTF8

Write-Host ""
Write-Host "✓ Commit message validation hook installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "The hook will automatically validate your commit messages." -ForegroundColor Cyan
Write-Host ""
Write-Host "To test it manually, run:" -ForegroundColor Yellow
Write-Host "  .\validate-commits.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To validate commits before pushing:" -ForegroundColor Yellow
Write-Host "  .\validate-commits.ps1 -Count 10" -ForegroundColor White
Write-Host ""
Write-Host "To uninstall, delete:" -ForegroundColor Yellow
Write-Host "  $hookFile" -ForegroundColor White
Write-Host ""
