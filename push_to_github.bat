@echo off
REM ============================================================
REM  HalluGuard — Push Replication Package to GitHub (Windows CMD)
REM ============================================================
REM  Run this script from inside the extracted "halluguard" folder.
REM  Replace YOUR-ORG and YOUR-REPO with your actual GitHub account
REM  and repository name before executing.
REM ============================================================

echo Step 1: Initialise local git repository
git init

echo Step 2: Configure user identity (skip if already set globally)
git config user.name "Your Name"
git config user.email "you@example.com"

echo Step 3: Add all files to staging
git add .

echo Step 4: Create the initial commit
git commit -m "Initial commit: HalluGuard replication package (INFSOF-D-25-01537)"

echo Step 5: Rename default branch to main
git branch -M main

echo Step 6: Add the remote GitHub repository
echo   --- create an EMPTY repo first at https://github.com/new ---
git remote add origin https://github.com/YOUR-ORG/YOUR-REPO.git

echo Step 7: Push to GitHub
git push -u origin main

echo ============================================================
echo  Done. Verify at: https://github.com/YOUR-ORG/YOUR-REPO
echo ============================================================
echo.
echo  OPTIONAL — Tag this release to mint a Zenodo DOI:
echo    git tag -a v1.0.0 -m "Camera-ready release for INFSOF"
echo    git push origin v1.0.0
echo  Then enable the GitHub-Zenodo integration at https://zenodo.org/account/settings/github/
echo ============================================================

pause
