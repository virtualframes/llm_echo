# Contributing to Jules 🤝

Thank you for your interest in contributing to Jules! This document provides guidelines for community participation in auditing LLM-related content.

## 🎯 Ways to Contribute

### 1. **Perform Manual Audits**

Review auto-generated audit templates and provide human judgment:

**Process:**
1. Check the `audit_templates/` directory for new audit templates
2. Review the flagged post and detection results
3. Fill out the community audit checklist
4. Submit your review as a GitHub issue or PR

**What to Check:**
- Is the consciousness/sentience claim unverified?
- Is the post part of a genuine discussion or echo chamber?
- Are there legitimate research references?
- Does the context change the interpretation?

### 2. **Review Flagged Content**

Help improve detection accuracy by validating results:

**False Positives:**
- Document posts incorrectly flagged as hallucinations
- Provide context for why the detection was incorrect
- Suggest improvements to detection algorithms

**False Negatives:**
- Report posts that should have been flagged but weren't
- Explain what patterns the detector missed
- Help expand the hallucination keyword list

### 3. **Improve Detection Algorithms**

Contribute code improvements:

**Areas for Enhancement:**
- Better NLP techniques for hallucination detection
- More sophisticated similarity metrics for echo detection
- Context-aware analysis
- Multi-language support

### 4. **Documentation**

Help improve documentation:
- Tutorial videos or guides
- Use case examples
- FAQ additions
- Translation to other languages

## 📝 Audit Template Guide

When reviewing an audit template, consider these questions:

### Hallucination Analysis
- [ ] Does the post make unverifiable claims about AI consciousness?
- [ ] Are there first-person consciousness claims from an AI?
- [ ] Does it conflate correlation with causation?
- [ ] Are quantum mysticism buzzwords used without scientific basis?

### Echo Chain Analysis
- [ ] Is this part of a coordinated or bot-generated campaign?
- [ ] Are the similar posts from the same author?
- [ ] Is this genuine repetition or coincidental similarity?
- [ ] Does the temporal pattern suggest organic discussion?

### Context Matters
- [ ] Is this satire, humor, or creative fiction?
- [ ] Is it part of a legitimate research discussion?
- [ ] Are there proper citations and qualifications?
- [ ] Is the author clearly distinguishing speculation from fact?

## 🔬 Detection Algorithm Guidelines

When contributing code for detection algorithms:

### Hallucination Detection
```python
# Good: Specific, contextual patterns
pattern = r'\bAI\s+(is|are)\s+definitely\s+(conscious|sentient)\b'

# Avoid: Overly broad patterns that catch legitimate discussion
pattern = r'\bAI\b.*\bconscious\b'  # Too broad!
```

### Echo Detection
- Balance sensitivity vs. specificity
- Consider temporal patterns
- Account for quote attribution
- Distinguish between legitimate discussion and echo chambers

## 🐛 Reporting Issues

### Bug Reports
Include:
- Jules version
- Python version
- Operating system
- Steps to reproduce
- Expected vs. actual behavior
- Relevant logs or error messages

### Feature Requests
Include:
- Clear use case description
- Why existing features don't address the need
- Proposed implementation approach (if applicable)
- Potential impact on existing functionality

## 💻 Code Contributions

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/virtualframes/llm_echo.git
cd llm_echo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

### Code Style

We follow PEP 8 with these specifics:
- Line length: 100 characters
- Use `black` for formatting
- Use `flake8` for linting
- Type hints encouraged but not required

```bash
# Format code
black jules tests

# Lint code
flake8 jules

# Run tests
pytest
```

### Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your feature/fix: `git checkout -b feature/your-feature-name`
3. **Write tests** for your changes
4. **Ensure all tests pass**: `pytest`
5. **Format and lint**: `black jules tests && flake8 jules`
6. **Update documentation** if needed
7. **Commit** with clear messages: `git commit -m "Add feature: description"`
8. **Push** to your fork: `git push origin feature/your-feature-name`
9. **Open a Pull Request** with:
   - Clear description of changes
   - Reference to related issues
   - Test results
   - Screenshots (for UI changes)

### Commit Message Guidelines

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(detector): add quantum mysticism pattern detection

Adds new patterns to detect quantum consciousness claims without
scientific basis.

Closes #42
```

## 🧪 Testing Guidelines

### Writing Tests

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **Test coverage**: Aim for >80% coverage
- **Mock external dependencies**: Use mocks for Reddit API calls

```python
# Good test structure
def test_specific_behavior():
    """Test that X does Y when Z"""
    # Arrange
    detector = HallucinationDetector(config)
    post = {'title': 'test', 'selftext': 'content'}
    
    # Act
    score, flags = detector.detect(post)
    
    # Assert
    assert score > 0
    assert len(flags) > 0
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_hallucination_detector.py

# Specific test
pytest tests/unit/test_hallucination_detector.py::TestHallucinationDetector::test_detect_consciousness_claim

# With coverage
pytest --cov=jules --cov-report=html
```

## 📊 Performance Guidelines

- Minimize Reddit API calls (respect rate limits)
- Cache results when appropriate
- Use efficient similarity algorithms
- Profile before optimizing

## 🔒 Security Guidelines

- Never commit API credentials
- Use environment variables for secrets
- Validate and sanitize all external input
- Follow principle of least privilege

## 📞 Getting Help

- **Questions**: [GitHub Discussions](https://github.com/virtualframes/llm_echo/discussions)
- **Bugs**: [GitHub Issues](https://github.com/virtualframes/llm_echo/issues)
- **Real-time**: Check README for community chat links

## 🌟 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Acknowledged in release notes
- Credited in relevant documentation

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Background
- Identity
- Beliefs (as long as contributions remain constructive and respectful)

### Expected Behavior

- Be respectful and considerate
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy toward other contributors

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or deliberate disruption
- Publishing others' private information
- Other conduct inappropriate in a professional setting

### Enforcement

Violations may result in:
1. Warning
2. Temporary ban
3. Permanent ban

Report issues to: [project maintainers]

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make Jules better! 🎉**

Every contribution, no matter how small, helps improve the accuracy and usefulness of this tool for the entire community.
