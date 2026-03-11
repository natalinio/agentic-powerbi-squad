# Contributing to Power BI AI Developer

Thank you for your interest in contributing to **Power BI AI Developer**! 🎉

This document provides guidelines and best practices for contributing to this project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)

---

## 📜 Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to andrea.natali@avanade.com.

---

## 🤝 How Can I Contribute?

### 1. Reporting Bugs

If you find a bug, please open an issue using the **[Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md)**.

Include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Environment details (Power BI version, Python version, OS)

### 2. Suggesting Features

Have an idea for improvement? Open an issue using the **[Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md)**.

Include:
- Clear use case description
- Why this feature is valuable
- Examples of how it would work

### 3. Improving Documentation

Documentation improvements are always welcome! This includes:
- Fixing typos or unclear explanations
- Adding examples or tutorials
- Translating documentation to other languages
- Improving reference files (`.github/references/`)

### 4. Contributing Code

We welcome code contributions for:
- New DAX patterns (`.github/references/dax-patterns.md`)
- New BPA rules (`.github/references/bpa-rules-reference.md`)
- New relationship patterns (`.github/references/relationship-patterns.md`)
- Bug fixes in Python scripts (`.github/scripts/`)
- Agent skill improvements (`.github/skills/`)

---

## 🛠️ Development Setup

### Prerequisites

- **Git**: Version control
- **Python 3.10+**: For scripts and testing
- **Power BI Desktop**: December 2025 or later (with preview features enabled)
- **VS Code**: Recommended editor (with GitHub Copilot extension)

### Installation Steps

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/PowerBI-AI-FullStack-Developer.git
   cd PowerBI-AI-FullStack-Developer
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/natalinio/PowerBI-AI-FullStack-Developer.git
   ```

4. **Create Python virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 📂 Project Structure

Understanding the structure is critical for effective contributions:

```
.github/
├── agents/              # Custom agent definitions (modify with caution)
├── skills/              # Step-by-step execution guides (11 files: 00-10)
├── references/          # Knowledge base (TMDL, DAX, BPA rules)
└── scripts/             # Universal Python tools (lineage fix, testing)

[ProjectName]/           # Template folder (DO NOT modify — copy structure for new projects)

<ProjectName>/           # Your project folders (create one per semantic model)
├── PBIP/                # PBIP canvas + TMDL files
├── data/                # Generated CSV mock data
├── scripts/             # Project-specific Python scripts
├── tests/               # Functional test artifacts
└── spec/                # User specifications
```

### What to Edit

| File/Folder | When to Edit |
|-------------|--------------|
| `.github/skills/` | Improve workflow steps or fix bugs in agent execution logic |
| `.github/references/` | Add new DAX patterns, BPA rules, relationship patterns, or TMDL syntax updates |
| `.github/scripts/` | Fix bugs or add features to universal Python tools |
| `spec/` | Maintain specification templates and examples |
| `README.md` | Improve documentation, fix typos, add examples |

### What NOT to Edit (Without Discussion)

- `.github/copilot-instructions.md` (global agent behavior)
- `.github/agents/powerbi-AI-developer.agent.md` (core agent definition)

For these files, **open an issue first** to discuss proposed changes.

---

## 🎨 Coding Standards

### Python Code

- **Style**: PEP 8 compliant (use `black` formatter)
- **Type Hints**: Use type annotations for function parameters and returns
- **Docstrings**: Required for all public functions (Google style)
- **Error Handling**: Use explicit `try/except` blocks with meaningful error messages

Example:
```python
def fix_lineage_tags(project_name: str) -> int:
    """
    Regenerate all lineageTag GUIDs with unique UUID v4 values.
    
    Args:
        project_name: Name of the project folder (e.g., 'SalesOverview')
        
    Returns:
        Number of lineageTags regenerated
        
    Raises:
        FileNotFoundError: If TMDL definition folder doesn't exist
    """
    # Implementation...
```

### TMDL Files

- **Indentation**: Use TAB characters ONLY (not spaces)
- **Naming Conventions**: Follow `.github/references/naming-conventions.md`
- **Validation**: Test in Power BI Desktop before committing

### DAX Code

- **Formatting**: VAR/RETURN pattern for all measures
- **Functions**: Use DIVIDE() instead of `/`
- **Performance**: Follow `.github/references/dax-optimization-framework.md`

### Markdown Documentation

- **Headers**: Use ATX-style (`#`, `##`, `###`)
- **Code Blocks**: Always specify language (```python, ```dax, ```powershell)
- **Links**: Use relative paths for internal links
- **Tables**: Use proper alignment (`:---:`, `:---`, `---:`)

---

## 🔄 Pull Request Process

### Before Submitting

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Test your changes**:
   - For Python scripts: Run existing tests + add new tests
   - For TMDL changes: Open in Power BI Desktop and validate
   - For DAX patterns: Verify with DAX Studio

3. **Update documentation**:
   - If you added a new feature, update `README.md`
   - If you modified a reference file, add examples

4. **Commit with meaningful messages**:
   ```bash
   git commit -m "feat: Add support for many-to-many relationships in TMDL"
   git commit -m "fix: Correct GUID collision in fix_lineage_tags.py"
   git commit -m "docs: Add example for fiscal year time intelligence"
   ```

   Use conventional commits format:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Formatting changes
   - `refactor:` Code restructuring
   - `test:` Adding tests
   - `chore:` Maintenance tasks

### Submitting the PR

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub

3. **Fill out the PR template** completely:
   - Description of changes
   - Related issues (use `Fixes #123` or `Closes #456`)
   - Type of change (bug fix, new feature, breaking change)
   - Testing performed
   - Screenshots (if UI/visual changes)

4. **Wait for review**:
   - Address reviewer comments
   - Keep PR scope focused (one feature/fix per PR)
   - Be responsive to feedback

### PR Review Criteria

- ✅ Code follows project conventions
- ✅ All tests pass
- ✅ Documentation is updated
- ✅ Commit messages are clear
- ✅ No merge conflicts with `main`
- ✅ PR description is complete

---

## 📝 Issue Guidelines

### Before Opening an Issue

1. **Search existing issues** to avoid duplicates
2. **Use the latest version** of the project
3. **Reproduce the issue** in a clean environment

### Issue Templates

Use the provided templates:
- **[Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)**: For bugs or errors
- **[Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)**: For new features or improvements

### Issue Labels

Maintainers will apply labels:
- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

---

## 🧪 Testing Guidelines

### Python Scripts

All Python scripts must have corresponding tests:

```powershell
# Run tests for specific script
pytest tests/test_fix_lineage_tags.py -v

# Run all tests
pytest tests/ -v
```

### Test Structure

```python
import pytest
from pathlib import Path
from fix_lineage_tags import fix_lineage_tags

def test_fix_lineage_tags_regenerates_guids():
    """Test that fix_lineage_tags generates unique GUIDs"""
    project_name = "TestProject"
    result = fix_lineage_tags(project_name)
    assert result > 0
    # Add assertions to verify GUID uniqueness
```

### TMDL Validation

After modifying TMDL templates or references:

1. Generate a test project with the agent
2. Open PBIP file in Power BI Desktop
3. Verify no parsing errors
4. Refresh data and validate relationships

### DAX Testing

For new DAX patterns:

1. Add pattern to `.github/references/dax-patterns.md`
2. Create test case in a test project
3. Validate with DAX Studio (query plan, performance)
4. Add to BPA rules if applicable

---

## 📚 Documentation Standards

### Reference Files (`.github/references/`)

- **Structure**: Use consistent heading hierarchy
- **Examples**: Include code examples for every pattern
- **Anti-Patterns**: Document what NOT to do (with ⛔ marker)
- **Links**: Reference official Microsoft documentation

### Skill Files (`.github/skills/`)

- **Step-by-Step**: Each skill must have numbered steps
- **Approval Gates**: Clearly mark where agent must STOP
- **Error Prevention**: Include ⛔ CRITICAL sections for common mistakes

### README Updates

- Keep **Quick Start** section under 5 minutes
- Update **Roadmap** when new features are added
- Add examples to **Usage** section for new patterns

---

## 🏅 Recognition

Contributors will be recognized in:
- **README.md**: Contributors section
- **Release Notes**: Acknowledgments for each version
- **GitHub Insights**: Contributor graph

---

## ❓ Questions?

If you have questions about contributing:

1. Check existing [issues](https://github.com/natalinio/PowerBI-AI-FullStack-Developer/issues)
2. Open a **question issue** with details
3. Email: andrea.natali@avanade.com

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the **MIT License**.

---

Thank you for contributing to Power BI AI Developer! 🚀

**Built with ❤️ by the community**
