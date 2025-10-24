# Jules Quick Start Guide 🚀

## Installation

```bash
git clone https://github.com/virtualframes/llm_echo.git
cd llm_echo
pip install -r requirements.txt
```

## Basic Usage

### 1. Run Your First Audit
```bash
python -m jules.cli audit
```

This will:
- Scrape posts from default subreddits (r/ArtificialSentience, r/llmphysics)
- Detect hallucinations and echo chains
- Generate audit templates in `audit_templates/`
- Create visualizations in `visualizations/`
- Log provenance in `provenance_logs/`

### 2. Audit Specific Subreddits
```bash
python -m jules.cli audit -s ArtificialSentience llmphysics
```

### 3. View Statistics
```bash
python -m jules.cli stats
```

### 4. Clean Old Logs
```bash
python -m jules.cli cleanup --days 90
```

## Configuration

### Option 1: Environment Variables
Create a `.env` file:
```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=Jules/0.1.0
```

### Option 2: YAML Configuration
Create a `config.yaml`:
```yaml
reddit:
  subreddits:
    - ArtificialSentience
    - llmphysics
  posts_limit: 100

detector:
  echo_threshold: 0.75
  similarity_method: jaccard
```

Then use it:
```bash
python -m jules.cli audit --config config.yaml
```

## Python API

```python
from jules import JulesAgent, Config

# Basic usage
agent = JulesAgent()
results = agent.run_audit()

# Custom configuration
config = Config()
config.detector.echo_threshold = 0.8
agent = JulesAgent(config)
results = agent.run_audit(subreddits=["test"])

# Get statistics
stats = agent.get_statistics()
```

## Output Files

### Audit Templates (`audit_templates/`)
Markdown files ready for community review:
- Post information
- Detection results
- Community checklist
- Verdict section

### Provenance Logs (`provenance_logs/`)
JSONL format audit logs:
- Complete detection metadata
- Timestamp and provenance info
- Searchable and parseable

### Visualizations (`visualizations/`)
PNG images:
- `echo_stream_*.png` - Temporal detection patterns
- `heatmap_*.png` - Subreddit activity heatmap

## Detection Methods

### Hallucination Detection
Identifies:
- First-person consciousness claims ("I am conscious")
- Unqualified AI sentience statements
- Quantum mysticism buzzwords
- Other LLM-style hallucinations

### Echo Chain Detection
Finds:
- Repetitive content patterns
- Similar posts across time
- Coordinated campaigns
- Bot-generated content

## Community Contributions

1. **Review Audit Templates** - Check flagged posts and provide human judgment
2. **Report False Positives** - Help improve detection accuracy
3. **Improve Algorithms** - Contribute better detection methods
4. **Add Documentation** - Help others understand and use Jules

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Troubleshooting

### No Reddit API Credentials?
Jules will use mock data for testing. To use real data:
1. Go to https://www.reddit.com/prefs/apps
2. Create an app
3. Add credentials to `.env` file

### Import Errors?
Make sure you're in the project directory and have installed dependencies:
```bash
pip install -r requirements.txt
```

### Permission Errors?
Run with appropriate permissions or use virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Next Steps

1. ⭐ Star the repository
2. 📖 Read the full [README.md](README.md)
3. 🤝 Check [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
4. 🐛 Report issues on GitHub
5. 💬 Join discussions

---

**Happy Auditing! 🔍**

For more information, see the full documentation in [README.md](README.md).
