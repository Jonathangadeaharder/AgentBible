#!/usr/bin/env pwsh
# Local Commit Message Validation Script
# Validates commit messages against rules/commit.md standards

param(
    [Parameter(Mandatory=$false)]
    [int]$Count = 10,
    
    [Parameter(Mandatory=$false)]
    [string]$Branch = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Hook = $false,
    
    [Parameter(Mandatory=$false)]
    [string]$CommitMsgFile = ""
)

# ANSI Color Codes
$script:Colors = @{
    Red = "`e[31m"
    Green = "`e[32m"
    Yellow = "`e[33m"
    Blue = "`e[34m"
    Magenta = "`e[35m"
    Cyan = "`e[36m"
    Bold = "`e[1m"
    Reset = "`e[0m"
}

# Valid commit types
$script:ValidTypes = @(
    'feat', 'fix', 'docs', 'style', 'refactor', 
    'perf', 'test', 'build', 'ci', 'chore'
)

# Statistics
$script:Stats = @{
    Total = 0
    Valid = 0
    Invalid = 0
    Warnings = 0
}

function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "Reset"
    )
    Write-Host "$($Colors[$Color])$Text$($Colors.Reset)"
}

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-ColorText "═══════════════════════════════════════════════════════════" "Cyan"
    Write-ColorText " $Text" "Bold"
    Write-ColorText "═══════════════════════════════════════════════════════════" "Cyan"
    Write-Host ""
}

function Write-Section {
    param([string]$Text)
    Write-Host ""
    Write-ColorText "───────────────────────────────────────────────────────────" "Blue"
    Write-ColorText " $Text" "Bold"
    Write-ColorText "───────────────────────────────────────────────────────────" "Blue"
}

function Get-CommitMessages {
    param(
        [int]$Count,
        [string]$Branch
    )
    
    if ($Branch) {
        $rangeSpec = "origin/$Branch..HEAD"
        $commits = git log $rangeSpec --format="%H%x00%s%x00%b%x00" 2>$null
    } else {
        $commits = git log -n $Count --format="%H%x00%s%x00%b%x00"
    }
    
    if (-not $commits) {
        return @()
    }
    
    $commitList = @()
    $commitBlocks = $commits -split "`0`0`0"
    
    foreach ($block in $commitBlocks) {
        if ([string]::IsNullOrWhiteSpace($block)) { continue }
        
        $parts = $block -split "`0"
        if ($parts.Count -ge 2 -and -not [string]::IsNullOrWhiteSpace($parts[0]) -and -not [string]::IsNullOrWhiteSpace($parts[1])) {
            $commitList += @{
                Hash = $parts[0].Trim()
                Subject = $parts[1].Trim()
                Body = if ($parts.Count -gt 2) { $parts[2].Trim() } else { "" }
            }
        }
    }
    
    return $commitList
}

function Test-ConventionalCommitFormat {
    param([string]$Subject)
    
    # Pattern: type(scope): subject or type: subject
    $pattern = '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\([a-z0-9\-]+\))?: .+'
    return $Subject -match $pattern
}

function Get-CommitComponents {
    param([string]$Subject)
    
    if ($Subject -match '^([a-z]+)(\(([a-z0-9\-]+)\))?: (.+)$') {
        return @{
            Type = $Matches[1]
            Scope = $Matches[3]
            Description = $Matches[4]
            Valid = $true
        }
    }
    
    return @{
        Type = ""
        Scope = ""
        Description = $Subject
        Valid = $false
    }
}

function Test-SubjectLength {
    param([string]$Subject)
    return $Subject.Length -le 50
}

function Test-ImperativeMood {
    param([string]$Description)
    
    # Common non-imperative patterns
    $nonImperativePatterns = @(
        '^(added|fixed|changed|updated|removed|deleted|created|modified)',
        '^(adds|fixes|changes|updates|removes|deletes|creates|modifies)',
        '^(adding|fixing|changing|updating|removing|deleting|creating|modifying)'
    )
    
    foreach ($pattern in $nonImperativePatterns) {
        if ($Description -match $pattern) {
            return $false
        }
    }
    
    return $true
}

function Test-SubjectCapitalization {
    param([string]$Description)
    
    # Should not start with capital letter (after type and scope)
    return -not ($Description -cmatch '^[A-Z]')
}

function Test-SubjectPeriod {
    param([string]$Description)
    
    # Should not end with period
    return -not ($Description -match '\.$')
}

function Test-BodyLineLength {
    param([string]$Body)
    
    if ([string]::IsNullOrWhiteSpace($Body)) {
        return $true
    }
    
    $lines = $Body -split "`n"
    foreach ($line in $lines) {
        if ($line.Trim().Length -gt 72) {
            return $false
        }
    }
    
    return $true
}

function Test-IssueReference {
    param(
        [string]$Subject,
        [string]$Body,
        [string]$Type
    )
    
    $fullMessage = "$Subject`n$Body"
    
    # Check for issue references
    $hasReference = $fullMessage -match '(Fixes|Closes|Refs?|Resolves|See) #\d+' -or
                    $fullMessage -match 'BREAKING CHANGE:'
    
    # Fixes should have issue references
    if ($Type -eq 'fix' -and -not $hasReference) {
        return @{
            HasReference = $false
            Required = $true
        }
    }
    
    return @{
        HasReference = $hasReference
        Required = $false
    }
}

function Test-AtomicCommit {
    param(
        [string]$Hash,
        [string]$Subject
    )
    
    # Get files changed in commit
    $filesChanged = git diff-tree --no-commit-id --name-only -r $Hash 2>$null
    
    if (-not $filesChanged) {
        return @{
            IsAtomic = $true
            Issues = @()
        }
    }
    
    $files = $filesChanged -split "`n" | Where-Object { $_ }
    $issues = @()
    
    # Check for mixed concerns
    $hasCode = $false
    $hasDocs = $false
    $hasTests = $false
    $hasConfig = $false
    
    foreach ($file in $files) {
        if ($file -match '\.(cs|cpp|py|js|jsx|ts|tsx)$') { $hasCode = $true }
        if ($file -match '\.(md|txt|rst)$') { $hasDocs = $true }
        if ($file -match 'test|spec') { $hasTests = $true }
        if ($file -match '\.(json|yml|yaml|toml|xml|config)$') { $hasConfig = $true }
    }
    
    # Check for mixed types
    $mixedCount = @($hasCode, $hasDocs, $hasTests, $hasConfig) | Where-Object { $_ } | Measure-Object | Select-Object -ExpandProperty Count
    
    if ($mixedCount -gt 2) {
        $issues += "Commit appears to mix multiple concerns (code, docs, tests, config)"
    }
    
    return @{
        IsAtomic = ($issues.Count -eq 0)
        Issues = $issues
        FileCount = $files.Count
    }
}

function Get-CommitQualityScore {
    param([hashtable]$Validation)
    
    $score = 100
    
    if (-not $Validation.FormatValid) { $score -= 30 }
    if (-not $Validation.TypeValid) { $score -= 20 }
    if (-not $Validation.LengthValid) { $score -= 10 }
    if (-not $Validation.ImperativeValid) { $score -= 15 }
    if (-not $Validation.CapitalizationValid) { $score -= 5 }
    if (-not $Validation.PeriodValid) { $score -= 5 }
    if (-not $Validation.BodyLengthValid) { $score -= 10 }
    if (-not $Validation.Atomic.IsAtomic) { $score -= 15 }
    if ($Validation.IssueRef.Required -and -not $Validation.IssueRef.HasReference) { $score -= 10 }
    
    return [Math]::Max(0, $score)
}

function Show-ValidationResults {
    param([hashtable]$Commit, [hashtable]$Validation)
    
    $shortHash = if ($Commit.Hash.Length -ge 7) { 
        $Commit.Hash.Substring(0, 7) 
    } else { 
        $Commit.Hash 
    }
    $score = Get-CommitQualityScore -Validation $Validation
    
    # Determine overall status
    $status = if ($score -eq 100) { "VALID" } 
              elseif ($score -ge 70) { "WARNING" } 
              else { "INVALID" }
    
    $statusColor = switch ($status) {
        "VALID" { "Green" }
        "WARNING" { "Yellow" }
        "INVALID" { "Red" }
    }
    
    Write-Host ""
    Write-ColorText "[$status] " $statusColor -NoNewline
    Write-Host "$shortHash - " -NoNewline
    Write-ColorText "$($Commit.Subject)" "Cyan"
    Write-Host "Quality Score: " -NoNewline
    Write-ColorText "$score/100" $(if ($score -ge 70) { "Green" } else { "Red" })
    
    # Show issues
    $issues = @()
    $warnings = @()
    
    if (-not $Validation.FormatValid) {
        $issues += "❌ Invalid format - must be: type(scope): subject"
        $issues += "   Example: feat(auth): add password reset functionality"
    }
    
    if (-not $Validation.TypeValid) {
        $issues += "❌ Invalid type '$($Validation.Components.Type)'"
        $issues += "   Valid types: $($ValidTypes -join ', ')"
    }
    
    if (-not $Validation.LengthValid) {
        $actualLength = $Commit.Subject.Length
        $issues += "❌ Subject too long ($actualLength characters, max 50)"
        $issues += "   Consider: $($Commit.Subject.Substring(0, [Math]::Min(47, $actualLength)))..."
    }
    
    if (-not $Validation.ImperativeValid) {
        $issues += "❌ Subject not in imperative mood"
        $issues += "   Use 'add' not 'added', 'fix' not 'fixed'"
    }
    
    if (-not $Validation.CapitalizationValid) {
        $issues += "❌ Subject description should not start with capital letter"
        $desc = $Validation.Components.Description
        if ($desc -and $desc.Length -gt 0) {
            $fixed = $desc.Substring(0,1).ToLower() + $(if ($desc.Length -gt 1) { $desc.Substring(1) } else { "" })
            $issues += "   Use: '$fixed' not '$desc'"
        }
    }
    
    if (-not $Validation.PeriodValid) {
        $issues += "❌ Subject should not end with period"
    }
    
    if (-not $Validation.BodyLengthValid) {
        $warnings += "⚠️  Body has lines exceeding 72 characters"
    }
    
    if (-not $Validation.Atomic.IsAtomic) {
        foreach ($issue in $Validation.Atomic.Issues) {
            $warnings += "⚠️  $issue"
        }
    }
    
    if ($Validation.IssueRef.Required -and -not $Validation.IssueRef.HasReference) {
        $warnings += "⚠️  Fix commit should reference an issue (e.g., 'Fixes #123')"
    }
    
    # Display issues
    if ($issues.Count -gt 0) {
        Write-Host ""
        Write-ColorText "Issues:" "Red"
        foreach ($issue in $issues) {
            Write-Host "  $issue"
        }
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-ColorText "Warnings:" "Yellow"
        foreach ($warning in $warnings) {
            Write-Host "  $warning"
        }
    }
    
    # Show suggestions
    if ($issues.Count -gt 0 -or $warnings.Count -gt 0) {
        Write-Host ""
        Write-ColorText "💡 Suggestions:" "Cyan"
        
        if (-not $Validation.FormatValid -or -not $Validation.TypeValid) {
            Write-Host "  • Review rules/commit.md for format guidelines"
            Write-Host "  • Use: type(scope): description format"
        }
        
        if (-not $Validation.Atomic.IsAtomic) {
            Write-Host "  • Consider splitting this commit into smaller, focused changes"
            Write-Host "  • Use: git reset HEAD~1, then git add -p for selective staging"
        }
        
        if ($Validation.IssueRef.Required -and -not $Validation.IssueRef.HasReference) {
            Write-Host "  • Add issue reference in commit body or footer"
            Write-Host "  • Use: git commit --amend to update the message"
        }
    }
    
    return @{
        Status = $status
        Score = $score
        IssueCount = $issues.Count
        WarningCount = $warnings.Count
    }
}

function Validate-Commit {
    param([hashtable]$Commit)
    
    $components = Get-CommitComponents -Subject $Commit.Subject
    
    $validation = @{
        FormatValid = Test-ConventionalCommitFormat -Subject $Commit.Subject
        TypeValid = $ValidTypes -contains $components.Type
        LengthValid = Test-SubjectLength -Subject $Commit.Subject
        ImperativeValid = Test-ImperativeMood -Description $components.Description
        CapitalizationValid = Test-SubjectCapitalization -Description $components.Description
        PeriodValid = Test-SubjectPeriod -Description $components.Description
        BodyLengthValid = Test-BodyLineLength -Body $Commit.Body
        Components = $components
        Atomic = Test-AtomicCommit -Hash $Commit.Hash -Subject $Commit.Subject
        IssueRef = Test-IssueReference -Subject $Commit.Subject -Body $Commit.Body -Type $components.Type
    }
    
    return $validation
}

function Show-Summary {
    Write-Header "VALIDATION SUMMARY"
    
    $validPercent = if ($Stats.Total -gt 0) { 
        [Math]::Round(($Stats.Valid / $Stats.Total) * 100, 1) 
    } else { 0 }
    
    Write-Host "Total commits analyzed: " -NoNewline
    Write-ColorText $Stats.Total "Bold"
    
    Write-Host "Valid commits:          " -NoNewline
    Write-ColorText "$($Stats.Valid) ($validPercent%)" "Green"
    
    Write-Host "Invalid commits:        " -NoNewline
    Write-ColorText $Stats.Invalid "Red"
    
    Write-Host "Commits with warnings:  " -NoNewline
    Write-ColorText $Stats.Warnings "Yellow"
    
    Write-Host ""
    
    if ($Stats.Invalid -eq 0 -and $Stats.Warnings -eq 0) {
        Write-ColorText "✓ All commits follow the standards!" "Green"
        Write-Host ""
        return $true
    } elseif ($Stats.Invalid -eq 0) {
        Write-ColorText "⚠ All commits are valid but some have warnings" "Yellow"
        Write-Host ""
        return $true
    } else {
        Write-ColorText "✗ Some commits need corrections" "Red"
        Write-Host ""
        return $false
    }
}

function Show-Examples {
    Write-Section "EXAMPLES OF GOOD COMMITS"
    
    $examples = @(
        @{
            Type = "feat"
            Example = "feat(auth): add password reset email template"
            Description = "New feature with clear scope"
        },
        @{
            Type = "fix"
            Example = "fix(payment): prevent duplicate charge on retry"
            Description = "Bug fix with specific issue"
        },
        @{
            Type = "refactor"
            Example = "refactor(orders): extract order validation logic"
            Description = "Code improvement without behavior change"
        },
        @{
            Type = "docs"
            Example = "docs(readme): update installation instructions"
            Description = "Documentation update"
        }
    )
    
    foreach ($ex in $examples) {
        Write-Host ""
        Write-ColorText "  $($ex.Example)" "Green"
        Write-Host "  → $($ex.Description)"
    }
    
    Write-Host ""
}

function Validate-CommitMsgFile {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-ColorText "Error: Commit message file not found: $FilePath" "Red"
        exit 1
    }
    
    $content = Get-Content $FilePath -Raw
    $lines = $content -split "`n"
    
    # Extract subject (first non-empty line)
    $subject = ($lines | Where-Object { $_.Trim() } | Select-Object -First 1).Trim()
    
    # Extract body (remaining lines after blank line)
    $bodyLines = @()
    $inBody = $false
    foreach ($line in $lines[1..($lines.Count-1)]) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            $inBody = $true
            continue
        }
        if ($inBody -and -not ($line -match '^#')) {
            $bodyLines += $line
        }
    }
    $body = $bodyLines -join "`n"
    
    $commit = @{
        Hash = "STAGED"
        Subject = $subject
        Body = $body
    }
    
    Write-Header "COMMIT MESSAGE VALIDATION (Pre-Commit Hook)"
    
    $validation = Validate-Commit -Commit $commit
    $results = Show-ValidationResults -Commit $commit -Validation $validation
    
    if ($results.Status -eq "INVALID") {
        Write-Host ""
        Write-ColorText "❌ Commit message validation failed!" "Red"
        Write-ColorText "Please fix the issues above and try again." "Yellow"
        Write-Host ""
        exit 1
    } elseif ($results.Status -eq "WARNING") {
        Write-Host ""
        Write-ColorText "⚠️  Commit has warnings but will proceed" "Yellow"
        Write-Host ""
        exit 0
    } else {
        Write-Host ""
        Write-ColorText "✓ Commit message is valid!" "Green"
        Write-Host ""
        exit 0
    }
}

# Main execution
try {
    # Hook mode - validate single commit message
    if ($Hook -and $CommitMsgFile) {
        Validate-CommitMsgFile -FilePath $CommitMsgFile
        exit 0
    }
    
    Write-Header "COMMIT MESSAGE VALIDATOR"
    
    Write-Host "Analyzing commit messages against rules/commit.md standards..."
    Write-Host ""
    
    # Get commits
    $commits = Get-CommitMessages -Count $Count -Branch $Branch
    
    if ($commits.Count -eq 0) {
        Write-ColorText "No commits found to validate." "Yellow"
        exit 0
    }
    
    Write-Host "Found $($commits.Count) commit(s) to validate"
    
    # Validate each commit
    foreach ($commit in $commits) {
        $validation = Validate-Commit -Commit $commit
        $results = Show-ValidationResults -Commit $commit -Validation $validation
        
        $Stats.Total++
        
        switch ($results.Status) {
            "VALID" { $Stats.Valid++ }
            "WARNING" { 
                $Stats.Valid++
                $Stats.Warnings++
            }
            "INVALID" { $Stats.Invalid++ }
        }
    }
    
    # Show summary
    $success = Show-Summary
    
    # Show examples if there were issues
    if (-not $success) {
        Show-Examples
    }
    
    # Exit with appropriate code
    exit $(if ($success) { 0 } else { 1 })
    
} catch {
    Write-ColorText "Error: $_" "Red"
    Write-Host $_.ScriptStackTrace
    exit 1
}
