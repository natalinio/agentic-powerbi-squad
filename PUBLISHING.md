# 🚀 Publishing Guide — AI Semantic Layer Builder

This guide explains how to publish this repository to GitHub and manage branches effectively.

---

## 📋 Pre-Publishing Checklist

Before publishing to GitHub, ensure:

- [x] All documentation files created (README.md, LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md)
- [x] Issue templates configured (.github/ISSUE_TEMPLATE/)
- [x] Pull request template created (.github/PULL_REQUEST_TEMPLATE.md)
- [x] .gitignore configured for Python, Power BI, and OS files
- [ ] All sensitive information removed (no credentials, API keys, or personal data)
- [ ] All files committed to local repository
- [ ] GitHub account ready (username: natalinio)

---

## 🌿 Branch Strategy

This project uses a **simplified branch strategy** optimized for solo/small-team development:

```
main (default branch)
  ├── feature/001-semantic-model-compiler
  ├── feature/002-report-generation
  ├── fix/lineage-tag-collision
  └── docs/update-readme
```

### Branch Types

| Prefix | Purpose | Example | Merge To |
|--------|---------|---------|----------|
| `feature/` | New features or enhancements | `feature/002-report-generation` | `main` |
| `fix/` | Bug fixes | `fix/lineage-tag-collision` | `main` |
| `docs/` | Documentation updates | `docs/update-contributing` | `main` |
| `refactor/` | Code restructuring (no new features) | `refactor/optimize-scripts` | `main` |
| `test/` | Test additions or improvements | `test/add-dax-validation` | `main` |

### Branch Naming Convention

- Use **lowercase** with hyphens
- Be **descriptive** but concise
- Include **issue number** if applicable: `feature/123-add-azure-sql`

---

## 📤 Publishing to GitHub

### Step 1: Initialize Local Repository (If Not Already Done)

```bash
cd c:\Users\andrea.natali\OneDrive - Avanade\Documents\Progetti\Avanade\Repos\aisemanticlayer
git init
git add .
git commit -m "Initial commit: AI Semantic Layer Builder v1.0"
```

### Step 2: Create GitHub Repository

1. Go to **https://github.com/natalinio**
2. Click **"New repository"**
3. Fill in details:
   - **Repository name**: `aisemanticlayer`
   - **Description**: "Build production-ready Power BI semantic models (PBIP/TMDL) from functional specifications using GitHub Copilot Custom Agent"
   - **Visibility**: ✅ **Public** (for open-source)
   - **Initialize**: ❌ Do NOT initialize with README, .gitignore, or license (we already have them)
4. Click **"Create repository"**

### Step 3: Link Local Repository to GitHub

```bash
# Add GitHub remote
git remote add origin https://github.com/natalinio/aisemanticlayer.git

# Verify remote
git remote -v
```

### Step 4: Push to GitHub

```bash
# Push main branch
git branch -M main
git push -u origin main
```

### Step 5: Configure Branch Protection (Recommended)

On GitHub:
1. Go to **Settings → Branches**
2. Click **"Add rule"** for `main` branch
3. Enable:
   - ✅ **Require a pull request before merging**
   - ✅ **Require approvals** (at least 1, if collaborating)
   - ✅ **Dismiss stale pull request approvals when new commits are pushed**
   - ✅ **Require conversation resolution before merging**
4. Save changes

---

## 🔄 Working with Feature Branches

### Creating a New Feature Branch

```bash
# Ensure you're on main and up-to-date
git checkout main
git pull origin main

# Create and switch to new feature branch
git checkout -b feature/002-report-generation
```

### Working on the Feature

```bash
# Make changes to files
# ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add Power BI Report definition generation to agent"

# Push to GitHub
git push -u origin feature/002-report-generation
```

### Opening a Pull Request

1. Go to **https://github.com/natalinio/aisemanticlayer**
2. Click **"Compare & pull request"** (appears after push)
3. Fill out the PR template:
   - Summary of changes
   - Related issues
   - Type of change
   - Testing performed
4. Click **"Create pull request"**

### Merging the Pull Request

After review and approval:

1. Click **"Squash and merge"** (recommended for clean history)
2. Delete the feature branch (select option after merge)

### Syncing Local Repository After Merge

```bash
# Switch back to main
git checkout main

# Pull latest changes
git pull origin main

# Delete local feature branch
git branch -d feature/002-report-generation
```

---

## 🏷️ Versioning Strategy

This project follows **Semantic Versioning** (SemVer):

### Version Format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)

### Examples

| Version | Description |
|---------|-------------|
| `1.0.0` | Initial public release (semantic model compiler) |
| `1.1.0` | Add report generation feature |
| `1.1.1` | Fix lineageTag collision bug |
| `2.0.0` | Breaking change: new agent invocation syntax |

### Creating a Release

When ready to release a new version:

```bash
# Tag the commit
git tag -a v1.0.0 -m "Release v1.0.0: Initial public release"

# Push tag to GitHub
git push origin v1.0.0
```

On GitHub:
1. Go to **Releases → Draft a new release**
2. Select the tag (`v1.0.0`)
3. Write release notes (describe new features, bug fixes, breaking changes)
4. Attach any binaries or artifacts (if applicable)
5. Click **"Publish release"**

---

## 🛠️ GitHub Repository Settings

### Recommended Settings

Navigate to **Settings** on GitHub:

#### General
- ✅ **Issues**: Enable (for bug reports and feature requests)
- ✅ **Projects**: Enable (for roadmap tracking)
- ✅ **Wiki**: Disable (use README and docs/ folder instead)
- ✅ **Sponsorships**: Enable (if you want to accept donations)

#### Features
- ✅ **Preserve this repository**: Enable (for archival)
- ✅ **Discussions**: Enable (for community Q&A)

#### Pull Requests
- ✅ **Allow squash merging** (keeps history clean)
- ❌ **Allow merge commits** (creates messy history)
- ❌ **Allow rebase merging** (can cause confusion for new contributors)
- ✅ **Automatically delete head branches** (after PR merge)

#### Security
- ✅ **Private vulnerability reporting**: Enable
- ✅ **Dependabot alerts**: Enable (for Python dependencies)

---

## 📊 GitHub Topics

Add relevant topics to help users discover your repository:

**Suggested topics**:
- `power-bi`
- `semantic-model`
- `pbip`
- `tmdl`
- `github-copilot`
- `custom-agent`
- `dax`
- `kimball`
- `dimensional-modeling`
- `ai-automation`
- `data-modeling`
- `business-intelligence`

Navigate to **Settings → Topics** and add these keywords.

---

## 📝 Post-Publication Tasks

After publishing:

1. **Update repository description** on GitHub (add homepage link if you have a docs site)
2. **Add badges** to README.md (license, build status, version)
3. **Share on social media** (LinkedIn, Twitter, Reddit r/PowerBI)
4. **Submit to awesome lists**: Search for "awesome power bi" or "awesome github copilot" repos
5. **Create initial GitHub Project** for roadmap tracking
6. **Enable GitHub Discussions** for community engagement

---

## 🎉 Congratulations!

Your repository is now live on GitHub! 🚀

**Repository URL**: https://github.com/natalinio/aisemanticlayer

**Next steps**:
- Monitor issues and pull requests
- Respond to community feedback
- Continue developing new features
- Update documentation as the project evolves

---

**Built with ❤️ by Andrea Natali**
