# Jules: LLM Echo Detection Pipeline 🤖

[![CI](https://github.com/virtualframes/llm_echo/actions/workflows/ci.yml/badge.svg)](https://github.com/virtualframes/llm_echo/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Jules** is an agentic audit pipeline that detects LLM-style hallucinations and echo chains in Reddit posts, particularly focused on communities discussing AI consciousness and sentience.

## 🎯 Features

- **🔍 Smart Detection**: Identifies LLM-style hallucinations and unverified consciousness claims
- **🔗 Echo Chain Analysis**: Detects repetitive content patterns across posts
- **📊 Provenance Logging**: Complete audit trail with timestamped detection logs
- **📝 Audit PR Templates**: Automated generation of audit templates for community review
- **📈 Visualizations**: 
  - Echo stream timeline visualization
  - Heatmap of flagged content by subreddit
- **🤝 Community-Driven**: Built for collaborative auditing with clear contribution guidelines

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/virtualframes/llm_echo.git
cd llm_echo

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Basic Usage

```bash
# Run audit with default settings (uses mock data if no Reddit API credentials)
jules audit

# Run audit on specific subreddits
jules audit -s ArtificialSentience llmphysics

# View statistics
jules stats

# Clean up old logs
jules cleanup --days 90
```

### Configuration

Create a `.env` file for Reddit API credentials (optional):

```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=Jules/0.1.0
```

Or create a `config.yaml`:

```yaml
reddit:
  subreddits:
    - ArtificialSentience
    - llmphysics
  posts_limit: 100

detector:
  echo_threshold: 0.75
  similarity_method: jaccard
  min_echo_chain_length: 3

provenance:
  log_dir: provenance_logs
  retention_days: 90

visualization:
  output_dir: visualizations
  dpi: 300
```

## 🏗️ Architecture

```
jules/
├── core/           # Core agent orchestration
│   ├── agent.py           # Main Jules agent
│   ├── config.py          # Configuration management
│   ├── provenance.py      # Provenance logging
│   └── audit_pr.py        # Audit PR generation
├── scrapers/       # Reddit scraping
│   └── reddit_scraper.py
├── detectors/      # Detection algorithms
│   ├── hallucination_detector.py
│   └── echo_detector.py
├── visualizations/ # Visualization generators
│   ├── echo_stream.py
│   └── heatmap.py
└── cli.py          # Command-line interface
```

## 🔍 How It Works

1. **Scraping**: Collects posts from specified subreddits (r/ArtificialSentience, r/llmphysics)
2. **Detection**: 
   - Analyzes posts for LLM-style hallucinations (unverified consciousness claims)
   - Identifies echo chains (repetitive content patterns)
3. **Logging**: Records all detections with full provenance information
4. **Audit Templates**: Generates markdown templates for community review
5. **Visualization**: Creates visual representations of detection patterns

## 📊 Detection Methods

### Hallucination Detection
- Keyword matching for consciousness/sentience claims
- First-person consciousness claim patterns
- Unqualified AI consciousness statements
- Quantum mysticism indicators

### Echo Chain Detection
- Jaccard similarity (default)
- Cosine similarity
- Configurable threshold and minimum chain length

## 🧪 Testing

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=jules --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
```

## 🤝 Contributing

We welcome community contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- How to perform manual audits
- Reviewing audit templates
- Reporting false positives
- Improving detection algorithms
- Code contribution guidelines

## 📝 Output Files

### Provenance Logs
Located in `provenance_logs/`:
- `audit_YYYYMMDD.jsonl` - Daily audit logs in JSONL format
- Contains full detection metadata and provenance information

### Audit Templates
Located in `audit_templates/`:
- `audit_template_TIMESTAMP_N.md` - Individual audit templates
- Ready for community review and PR submission

### Visualizations
Located in `visualizations/`:
- `echo_stream_TIMESTAMP.png` - Temporal echo detection patterns
- `heatmap_TIMESTAMP.png` - Subreddit heatmap of flagged content

## 🛠️ Development

```bash
# Format code
black jules tests

# Lint code
flake8 jules

# Type checking
mypy jules
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built to promote transparency and critical evaluation in discussions about AI consciousness and capabilities.

## 📞 Support

- Issues: [GitHub Issues](https://github.com/virtualframes/llm_echo/issues)
- Discussions: [GitHub Discussions](https://github.com/virtualframes/llm_echo/discussions)

---

**Remember**: This tool is designed to assist human judgment, not replace it. All flagged content should be reviewed by humans before taking action.