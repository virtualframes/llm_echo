"""Integration tests for Jules agent"""

import pytest
from jules import JulesAgent, Config
from jules.core.config import DetectorConfig, RedditConfig


class TestJulesAgent:
    """Integration tests for Jules agent"""

    @pytest.fixture
    def agent(self):
        """Create Jules agent instance"""
        config = Config()
        return JulesAgent(config)

    def test_run_audit_basic(self, agent):
        """Test basic audit run"""
        # Run audit (will use mock data if no Reddit credentials)
        results = agent.run_audit()

        assert "total_posts" in results
        assert "flagged_posts" in results
        assert "subreddits" in results
        assert "timestamp" in results

    def test_run_audit_specific_subreddits(self, agent):
        """Test audit with specific subreddits"""
        results = agent.run_audit(subreddits=["test"])

        assert results["subreddits"] == ["test"]

    def test_get_statistics(self, agent):
        """Test statistics retrieval"""
        # Run an audit first to generate some data
        agent.run_audit()

        # Get statistics
        stats = agent.get_statistics()

        assert "total_flagged" in stats
        assert "by_subreddit" in stats
        assert "avg_hallucination_score" in stats

    def test_audit_creates_artifacts(self, agent, tmp_path):
        """Test that audit creates expected artifacts"""
        # Update config to use temp directories
        agent.config.provenance.log_dir = str(tmp_path / "logs")
        agent.config.visualization.output_dir = str(tmp_path / "viz")

        # Update the loggers to use the new paths
        from pathlib import Path
        from jules.core.provenance import ProvenanceLogger
        from jules.visualizations.echo_stream import EchoStreamVisualizer
        from jules.visualizations.heatmap import HeatmapVisualizer

        agent.provenance_logger = ProvenanceLogger(agent.config.provenance)
        agent.echo_stream_viz = EchoStreamVisualizer(agent.config.visualization)
        agent.heatmap_viz = HeatmapVisualizer(agent.config.visualization)

        # Run audit
        results = agent.run_audit()

        # Check that logs were created
        log_dir = tmp_path / "logs"
        assert log_dir.exists(), "Provenance log directory should be created"

        # If posts were flagged, check visualizations
        if results["flagged_posts"] > 0:
            viz_dir = tmp_path / "viz"
            assert viz_dir.exists() or not results.get("visualizations")
