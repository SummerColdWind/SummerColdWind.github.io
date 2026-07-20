# Deploy academic homepage to GitHub Pages (user site: <username>.github.io)
# Usage: .\scripts\deploy.ps1
# Prerequisite: gh auth login

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

$User = (gh api user -q .login).Trim()
$Repo = "$User.github.io"
$FullName = "$User/$Repo"
$RemoteUrl = "https://github.com/$User/$Repo.git"

Write-Host "GitHub user: $User"
Write-Host "Target repo: $Repo"
Write-Host ""

python scripts/build.py

git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Deploy: update site and deployment scripts"
    Write-Host "Committed pending changes."
} else {
    Write-Host "No new commits needed."
}

function Test-GhRepo {
    param([string]$Name)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    gh repo view $Name --json name -q .name 2>$null | Out-Null
    $ok = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $prev
    return $ok
}

$repoExists = Test-GhRepo $FullName

if (-not $repoExists) {
    Write-Host "Creating GitHub repo $FullName ..."
    $remotes = @(git remote)
    if ($remotes -contains "origin") {
        git remote remove origin
    }
    gh repo create $Repo --public --description "Academic homepage" --source=. --remote=origin --push
    if ($LASTEXITCODE -ne 0) {
        throw "gh repo create failed."
    }
} else {
    Write-Host "Repo exists; pushing to origin ..."
    $remotes = @(git remote)
    if ($remotes -notcontains "origin") {
        git remote add origin $RemoteUrl
    } else {
        $current = (git remote get-url origin).Trim()
        if ($current -ne $RemoteUrl) {
            git remote set-url origin $RemoteUrl
        }
    }
    git push -u origin main
    if ($LASTEXITCODE -ne 0) {
        throw "git push failed."
    }
}

Write-Host "Enabling GitHub Pages ..."
gh api "repos/$FullName/pages" -X POST `
    -f build_type=legacy `
    -f "source[branch]=main" `
    -f "source[path]=/" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    gh api "repos/$FullName/pages" -X PUT `
        -f build_type=legacy `
        -f "source[branch]=main" `
        -f "source[path]=/" 2>$null | Out-Null
}

Write-Host ""
Write-Host "Done. Site URL (may take 1-3 min):"
Write-Host "  https://$User.github.io/"
Write-Host "  https://$User.github.io/zh/"
