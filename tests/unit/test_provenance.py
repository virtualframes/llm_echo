"""Unit tests for provenance logging"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from jules.core.provenance import ProvenanceLogger
from jules.core.config import ProvenanceConfig


class TestProvenanceLogger:
    """Test provenance logging functionality"""

    @pytest.fixture
    def temp_log_dir(self, tmp_path):
        """Create temporary log directory"""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        return log_dir

    @pytest.fixture
    def logger(self, temp_log_dir):
        """Create provenance logger instance"""
        config = ProvenanceConfig(log_dir=str(temp_log_dir))
        return ProvenanceLogger(config)

    @pytest.fixture
    def sample_flagged_post(self):
        """Create sample flagged post"""
        return {
            "post": {
                "id": "test123",
                "title": "Test post",
                "subreddit": "test",
                "author": "testuser",
                "url": "https://reddit.com/test",
            },
            "hallucination_score": 0.8,
            "hallucination_flags": ["flag1", "flag2"],
            "echo_score": 0.6,
            "echo_chains": [{"id": "other1"}, {"id": "other2"}],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def test_log_creates_file(self, logger, sample_flagged_post):
        """Test that logging creates a file"""
        log_path = logger.log(sample_flagged_post)

        assert Path(log_path).exists(), "Log file should exist"

    def test_log_contains_valid_json(self, logger, sample_flagged_post):
        """Test that log contains valid JSON"""
        log_path = logger.log(sample_flagged_post)

        with open(log_path, "r") as f:
            line = f.readline()
            entry = json.loads(line)

        assert entry["post_id"] == "test123"
        assert entry["hallucination_score"] == 0.8

    def test_get_statistics(self, logger, sample_flagged_post):
        """Test statistics retrieval"""
        # Log some entries
        logger.log(sample_flagged_post)
        logger.log(sample_flagged_post)

        stats = logger.get_statistics()

        assert stats["total_flagged"] == 2
        assert "by_subreddit" in stats
        assert "test" in stats["by_subreddit"]

    def test_cleanup_old_logs(self, logger, temp_log_dir):
        """Test cleanup of old logs"""
        # Create an old log file
        old_date = (datetime.now(timezone.utc) - timedelta(days=100)).strftime("%Y%m%d")
        old_file = temp_log_dir / f"audit_{old_date}.jsonl"
        old_file.write_text('{"test": "data"}\n')

        # Cleanup logs older than 90 days
        deleted = logger.cleanup_old_logs(days=90)

        assert deleted == 1, "Should delete 1 old log file"
        assert not old_file.exists(), "Old file should be deleted"
