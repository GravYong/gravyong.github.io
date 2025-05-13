---
# title: "sacra_git"
# layout: default
excerpt: 
sitemap: false
permalink: /sacra_git/
date: 2024-12-20
modified: 2024-12-20
tags: animation
# header:
#     overlay_image: header.png
#     overlay_filter: 0.1 
---


# SACRA Development Workflow

This document outlines the **standard Git workflow** for all contributors to the SACRA codebase. It ensures the `main` branch remains stable, and collaborative work proceeds smoothly.

---

## Main Branch Protection Policy (to be determined by Kiuchi-san)

- The `main` branch is protected.
- **No direct push is allowed** to `main`.
- All changes must go through **pull requests** and be **approved by Kenta Kiuchi before merging.
- Contributors **must update their local `main`** before merging anything.

---

## Standard Git Workflow

Follow the steps below for every new development or bugfix:

### 1. Clone the Repository (only once)
```bash
git clone https://github.com/YOUR-ACCOUNT/sacra.git
cd sacra
```

---

### 2. Always Start with a Clean, Updated `main`
```bash
git checkout main
git pull origin main   # This step is mandatory before merging
```

>  Never skip `git pull`. This ensures your `main` is up to date and avoids merge conflicts or overwriting others’ changes.

---

### 3. Create a New Branch for Your Work
```bash
git checkout -b your-branch-name
```

Use descriptive names like:
- `kota`


---

### 4. Make Changes and Commit
```bash
git add .
git commit -m "Describe your changes clearly"
```

---

### 5. Push Your Branch to GitHub
```bash
git push origin your-branch-name
```

---

### 6. Merge Back to `main` 

#### Case A:No Restrictions 
If you prefer local merging:

```bash
git checkout main
git pull origin main       # Important!
git merge your-branch-name
git push origin main
```
if you prefer pull request:

- Go to the GitHub repo page.
- Click **“Compare & pull request”**.
- Fill in the PR title and description.
- Submit the PR.
- If you have write access, you can click “Merge pull request” immediately without needing approval.


#### Case B: If restrictions are **enabled** (e.g., main branch protection):

1. Go to the GitHub repo page.
2. Click **“Compare & pull request”**.
3. Fill in the PR title and description.
4. Submit and wait for approval by **@kenta kiuchi**.
5. After approval, click **“Merge pull request”**.


---

### 7. (Optional) Delete Merged Branch
```bash
git branch -d your-branch-name          # local
git push origin --delete your-branch-name  # remote
```

---

## Summary

| Task | Command |
|------|---------|
| Update main | `git checkout main && git pull origin main` |
| Create new branch | `git checkout -b my-feature` |
| Merge into main | `git checkout main && git merge my-feature` |
| Push to GitHub | `git push origin main` |

---
