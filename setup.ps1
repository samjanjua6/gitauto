# Setup script to link this repo to GitHub
param (
    [string]$RemoteUrl
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  GitHub Streak Keeper - Setup Assistant  " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "[1/4] Initializing Git repository..." -ForegroundColor Yellow
    git init -b main
} else {
    Write-Host "[1/4] Git repository already initialized." -ForegroundColor Green
}

# Configure local git user
Write-Host "[2/4] Setting Git author profile..." -ForegroundColor Yellow
git config user.name "Shaheer ul Hassan"
git config user.email "samjanjua6@gmail.com"

# Stage and initial commit
Write-Host "[3/4] Staging files and creating initial commit..." -ForegroundColor Yellow
git add .
git commit -m "feat: initial commit for automated streak keeper" 2>$null

# Remote configuration
if (-not $RemoteUrl) {
    Write-Host ""
    $RemoteUrl = Read-Host "Enter your new GitHub repository URL (e.g. https://github.com/USERNAME/streak-keeper.git)"
}

if ($RemoteUrl) {
    Write-Host "[4/4] Setting remote origin and pushing to GitHub..." -ForegroundColor Yellow
    git remote remove origin 2>$null
    git remote add origin $RemoteUrl
    git branch -M main
    git push -u origin main
    Write-Host "`nRepository pushed successfully to GitHub!" -ForegroundColor Green
    Write-Host "GitHub Actions will now automatically keep your streak alive." -ForegroundColor Green
} else {
    Write-Host "`nNo remote URL provided. When ready, run:" -ForegroundColor Yellow
    Write-Host "  git remote add origin <YOUR_GITHUB_REPO_URL>" -ForegroundColor Gray
    Write-Host "  git branch -M main" -ForegroundColor Gray
    Write-Host "  git push -u origin main" -ForegroundColor Gray
}
