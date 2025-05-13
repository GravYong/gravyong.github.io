---
title: false
excerpt: 
sitemap: false
permalink: /sacra_git/
date: 2024-12-20
modified: 2024-12-20
tags: notes
---

# SACRA Development Workflow

This document outlines the **standard Git workflow** for all contributors to the SACRA codebase. It ensures the `main` branch remains stable, and collaborative work proceeds smoothly.

---

## Main Branch Protection Policy (to be determined by Kiuchi-san)

- The `main` branch is protected.
- **No direct push is allowed** to `main`.
- All changes must go through **pull requests** and be **approved by Kenta Kiuchi** before merging.
- Contributors **must update their local `main`** before merging anything.

---

## Standard Git Workflow

Follow the steps below for every new development or bugfix.

### 1. Clone the Repository (only once)

```bash
git clone https://github.com/YOUR-ACCOUNT/sacra.git
cd sacra
```

### 2. Always Start with a Clean, Updated `main`

```bash
git checkout main
git pull origin main   # This step is mandatory before merging
```

> Never skip `git pull`. This ensures your `main` is up to date and avoids merge conflicts or overwriting others’ changes.

### 3. Create a New Branch for Your Work

```bash
git checkout -b your-branch-name
```

Use descriptive names like: `kota_BHNS`, etc.

### 4. Make Changes and Commit

```bash
git add .
git commit -m "Describe your changes clearly"
```

### 5. Push Your Branch to GitHub

```bash
git push origin your-branch-name
```

---

## Merge Back to `main`

### Case A: No Restrictions

#### Option 1: Merge Locally

```bash
git checkout main
git pull origin main
git merge your-branch-name
git push origin main
```

#### Option 2: Create a Pull Request

- Go to the GitHub repo page.
- Click **“Compare & pull request”**.
- Fill in the PR title and description.
- Submit the PR.
- If you have write access, you can click **“Merge pull request”** immediately.

### Case B: Restrictions Enabled (e.g., branch protection)

- Go to the GitHub repo page.
- Click **“Compare & pull request”**.
- Fill in the PR title and description.
- Submit and wait for approval by **@kenta kiuchi**.
- After approval, click **“Merge pull request”**.

---

## (Optional) Delete Merged Branch

```bash
git branch -d your-branch-name          # local
git push origin --delete your-branch-name  # remote
```

---

## Summary Table

| Task | Command |
|------|---------|
| Update main | `git checkout main && git pull origin main` |
| Create new branch | `git checkout -b my-feature` |
| Merge into main | `git checkout main && git merge my-feature` |
| Push to GitHub | `git push origin main` |
