# Contributing to Mifos Loan Summarizer

Thank you for your interest in contributing to Mifos Loan Summarizer! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

---

## 📜 Code of Conduct

This project adheres to the Mifos Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@mifos.org.

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members
- Accept constructive criticism gracefully

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- A GitHub account
- (Optional) Docker Desktop

### Your First Contribution

Looking for a good first issue? Check out issues labeled:
- `good first issue` - Perfect for newcomers
- `help wanted` - We need community help
- `documentation` - Improve our docs

---

## 💻 Development Setup

### 1. Fork the Repository

Click the "Fork" button on GitHub to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/mifos-loan-summarizer.git
cd mifos-loan-summarizer
git remote add upstream https://github.com/hopessugar/mifos-loan-summarizer.git
```

### 3. Create Development Environment

#### Backend Setup

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

#### Frontend Setup

```bash
cd frontend
npm install
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 5. Verify Setup

```bash
# Test backend
cd backend
pytest

# Test frontend build
cd frontend
npm run build
```

---

## 🔧 Making Changes

### Branch Naming Convention

Use descriptive branch names:

```
feature/add-spanish-translation
fix/pdf-upload-timeout
docs/update-readme
refactor/extract-validation-logic
test/add-integration-tests
```

### Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### Keep Your Fork Updated

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

---

## ✅ Testing Guidelines

### Running Tests

#### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_validator.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

#### Frontend Tests

```bash
cd frontend

# Run tests (when implemented)
npm test

# Build check
npm run build
```

### Writing Tests

**All new features must include tests!**

#### Backend Test Example

```python
# tests/test_your_feature.py
import pytest
from your_module import your_function

def test_your_function_success():
    """Test successful case."""
    result = your_function(valid_input)
    assert result == expected_output

def test_your_function_error():
    """Test error handling."""
    with pytest.raises(ValueError):
        your_function(invalid_input)
```

#### Test Coverage Requirements

- New code: 80% minimum coverage
- Bug fixes: Add test that would have caught the bug
- Refactoring: Maintain or improve existing coverage

---

## 🎨 Code Style

### Python (Backend)

We follow **PEP 8** with some modifications:

```python
# Good
def extract_loan_amount(contract_text: str) -> Decimal:
    """Extract loan amount from contract text.
    
    Args:
        contract_text: The contract text to parse.
        
    Returns:
        The extracted loan amount.
        
    Raises:
        ValueError: If amount cannot be extracted.
    """
    # Implementation
    pass

# Bad
def extract(txt):  # Missing type hints and docstring
    return some_value
```

**Use Ruff for linting:**

```bash
cd backend
ruff check .
```

### JavaScript/React (Frontend)

Follow the existing ESLint configuration:

```javascript
// Good
export function AnalysisView({ result }) {
  const [expanded, setExpanded] = useState(false)
  
  return (
    <div className="analysis-container">
      {/* Component content */}
    </div>
  )
}

// Bad
function analysisview(props) {  // Wrong naming, no destructuring
  // Implementation
}
```

**Run ESLint:**

```bash
cd frontend
npm run lint
```

### General Principles

- **Descriptive names**: `calculate_total_interest` not `calc_ti`
- **Keep functions small**: <50 lines ideally
- **Document complex logic**: Add comments explaining "why", not "what"
- **Avoid magic numbers**: Use named constants
- **Error handling**: Always handle exceptions gracefully

---

## 📝 Commit Guidelines

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling

### Examples

```bash
# Good commits
git commit -m "feat(extractor): Add support for Hindi language contracts"
git commit -m "fix(validator): Correct EMI calculation for flat rate loans"
git commit -m "docs(readme): Update installation instructions for Windows"
git commit -m "test(pipeline): Add integration tests for full extraction flow"

# Bad commits
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "updates"
```

### Commit Best Practices

- One logical change per commit
- Write clear, descriptive messages
- Reference issues: `Fixes #123` or `Relates to #456`
- Keep commits atomic and reversible

---

## 🔀 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts with main branch
- [ ] Commit messages follow convention

### Creating a Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open Pull Request on GitHub:**
   - Click "New Pull Request"
   - Select your branch
   - Fill in the template

3. **PR Title Format:**
   ```
   feat(scope): Brief description of changes
   ```

### Pull Request Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally

## Screenshots (if applicable)
Add screenshots for UI changes.

## Related Issues
Fixes #123
```

### Review Process

1. **Automated checks** run (tests, linting)
2. **Maintainer review** (usually within 2-3 days)
3. **Address feedback** if requested
4. **Approval & merge** by maintainer

### After Your PR is Merged

- Delete your branch: `git branch -d feature/your-feature-name`
- Update your fork: `git pull upstream main`
- Celebrate! 🎉

---

## 🐛 Issue Guidelines

### Before Creating an Issue

1. **Search existing issues** - Your issue may already be reported
2. **Check documentation** - Make sure it's not a configuration issue
3. **Try latest version** - The bug may be fixed already

### Bug Report Template

```markdown
**Describe the Bug**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
Add screenshots if applicable.

**Environment:**
- OS: [e.g., Windows 11]
- Python Version: [e.g., 3.11.5]
- Node Version: [e.g., 20.10.0]
- Browser: [e.g., Chrome 120]

**Additional Context**
Any other relevant information.
```

### Feature Request Template

```markdown
**Problem Description**
What problem does this feature solve?

**Proposed Solution**
Your proposed solution.

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Any mockups, examples, or additional info.
```

---

## 🏷️ Labels

### Priority Labels
- `priority: critical` - Security, data loss, or system down
- `priority: high` - Major functionality broken
- `priority: medium` - Minor bug or enhancement
- `priority: low` - Nice-to-have features

### Type Labels
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to docs
- `question` - Questions about the project

### Status Labels
- `needs: triage` - Needs maintainer review
- `needs: info` - Awaiting more information
- `in: progress` - Someone is working on it
- `blocked` - Cannot proceed due to dependency

---

## 💡 Development Tips

### Common Tasks

**Add a new LLM provider:**
1. Create `backend/providers/your_provider.py`
2. Inherit from `BaseLLMProvider`
3. Implement required methods
4. Register in `providers/registry.py`
5. Add tests in `tests/test_integration_providers.py`
6. Update documentation

**Add a new validation rule:**
1. Add function in `backend/pipeline/validator.py`
2. Call from `validate_extraction()`
3. Add tests in `tests/test_validator.py`
4. Document in risk scoring section

**Add a new route:**
1. Create or update router in `backend/routers/`
2. Add to `backend/main.py`
3. Add tests in `tests/test_*.py`
4. Update OpenAPI documentation

### Debugging Tips

**Backend:**
```python
# Add logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Debug info: {variable}")

# Use debugger
import pdb; pdb.set_trace()
```

**Frontend:**
```javascript
// Console logging
console.log('Debug:', variable)

// React DevTools
// Install browser extension for component inspection
```

---

## 📚 Additional Resources

- [Project Wiki](https://github.com/hopessugar/mifos-loan-summarizer/wiki)
- [Mifos Developer Guide](https://mifos.org/developers/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Python Testing with Pytest](https://docs.pytest.org/)

---

## ❓ Questions?

- Join our [Discord Community](https://discord.gg/mifos)
- Email the maintainers: dev@mifos.org
- Open a [Discussion](https://github.com/hopessugar/mifos-loan-summarizer/discussions)

---

## 🎉 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

Happy Coding! 🚀
