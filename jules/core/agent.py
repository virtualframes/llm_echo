"""Main Jules agent orchestrator"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

from jules.core.config import Config
from jules.scrapers.reddit_scraper import RedditScraper
from jules.detectors.hallucination_detector import HallucinationDetector
from jules.detectors.echo_detector import EchoDetector
from jules.core.provenance import ProvenanceLogger
from jules.visualizations.echo_stream import EchoStreamVisualizer
from jules.visualizations.heatmap import HeatmapVisualizer
from jules.core.audit_pr import AuditPRGenerator

logger = logging.getLogger(__name__)


class JulesAgent:
    """
    Jules: Agentic Audit Pipeline

    Orchestrates the entire audit process:
    1. Scrapes Reddit posts from specified subreddits
    2. Detects LLM-style hallucinations and echo chains
    3. Logs provenance information
    4. Generates audit PR templates
    5. Creates visualizations
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.scraper = RedditScraper(self.config.reddit)
        self.hallucination_detector = HallucinationDetector(self.config.detector)
        self.echo_detector = EchoDetector(self.config.detector)
        self.provenance_logger = ProvenanceLogger(self.config.provenance)
        self.echo_stream_viz = EchoStreamVisualizer(self.config.visualization)
        self.heatmap_viz = HeatmapVisualizer(self.config.visualization)
        self.pr_generator = AuditPRGenerator()

        # Ensure output directories exist
        os.makedirs(self.config.provenance.log_dir, exist_ok=True)
        os.makedirs(self.config.visualization.output_dir, exist_ok=True)

    def run_audit(self, subreddits: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run complete audit pipeline

        Args:
            subreddits: List of subreddit names to audit (overrides config)

        Returns:
            Dictionary containing audit results and statistics
        """
        logger.info("🤖 Jules: Starting audit pipeline...")

        # Use provided subreddits or default from config
        target_subreddits = subreddits or self.config.reddit.subreddits

        # Step 1: Scrape posts
        logger.info(f"📡 Scraping posts from: {', '.join(target_subreddits)}")
        posts = self.scraper.scrape_posts(target_subreddits)
        logger.info(f"✓ Scraped {len(posts)} posts")

        # Step 2: Detect hallucinations and echo chains
        logger.info("🔍 Detecting hallucinations and echo chains...")
        flagged_posts = []

        for post in posts:
            # Detect hallucinations
            hallucination_score, hallucination_flags = self.hallucination_detector.detect(post)

            # Detect echo chains
            echo_score, echo_chains = self.echo_detector.detect(post, posts)

            # Flag post if issues detected
            if hallucination_score > 0.5 or len(echo_chains) > 0:
                flagged_post = {
                    "post": post,
                    "hallucination_score": hallucination_score,
                    "hallucination_flags": hallucination_flags,
                    "echo_score": echo_score,
                    "echo_chains": echo_chains,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                flagged_posts.append(flagged_post)

                # Log provenance
                self.provenance_logger.log(flagged_post)

        logger.info(f"⚠️  Flagged {len(flagged_posts)} posts")

        # Step 3: Generate audit PRs for flagged claims
        if flagged_posts:
            logger.info("📝 Generating audit PR templates...")
            pr_files = self.pr_generator.generate_prs(flagged_posts)
            logger.info(f"✓ Generated {len(pr_files)} audit templates")

        # Step 4: Create visualizations
        logger.info("📊 Creating visualizations...")
        viz_files = {}

        if flagged_posts:
            # Echo stream visualization
            echo_stream_file = self.echo_stream_viz.create(flagged_posts, posts)
            viz_files["echo_stream"] = echo_stream_file

            # Heatmap visualization
            heatmap_file = self.heatmap_viz.create(flagged_posts, target_subreddits)
            viz_files["heatmap"] = heatmap_file

            logger.info(f"✓ Created visualizations: {', '.join(viz_files.keys())}")

        # Compile results
        results = {
            "total_posts": len(posts),
            "flagged_posts": len(flagged_posts),
            "subreddits": target_subreddits,
            "timestamp": datetime.utcnow().isoformat(),
            "visualizations": viz_files,
            "flagged_details": flagged_posts,
        }

        logger.info("✅ Audit pipeline completed!")
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get audit statistics from provenance logs"""
        return self.provenance_logger.get_statistics()
