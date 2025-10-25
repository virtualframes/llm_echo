"""Provenance logging system"""

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ProvenanceLogger:
    """Logs provenance information for all flagged posts"""

    def __init__(self, config):
        self.config = config
        self.log_dir = Path(config.log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, flagged_post: Dict[str, Any]) -> str:
        """
        Log a flagged post with provenance information

        Args:
            flagged_post: Dictionary containing post and detection results

        Returns:
            Path to log file
        """
        timestamp = datetime.now(timezone.utc)
        date_str = timestamp.strftime("%Y%m%d")
        log_filename = f"audit_{date_str}.jsonl"
        log_path = self.log_dir / log_filename

        # Create log entry
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "post_id": flagged_post["post"].get("id", "unknown"),
            "subreddit": flagged_post["post"].get("subreddit", "unknown"),
            "author": flagged_post["post"].get("author", "unknown"),
            "title": flagged_post["post"].get("title", ""),
            "hallucination_score": flagged_post["hallucination_score"],
            "hallucination_flags": flagged_post["hallucination_flags"],
            "echo_score": flagged_post["echo_score"],
            "echo_chain_count": len(flagged_post["echo_chains"]),
            "url": flagged_post["post"].get("url", ""),
            "provenance": {
                "detector_version": "0.1.0",
                "method": self.config.__class__.__name__,
                "config": {
                    "echo_threshold": getattr(self.config, "echo_threshold", None),
                    "similarity_method": getattr(self.config, "similarity_method", None),
                },
            },
        }

        # Append to log file (JSONL format)
        with open(log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        logger.debug(f"Logged provenance for post {log_entry['post_id']} to {log_path}")
        return str(log_path)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregate statistics from provenance logs

        Returns:
            Dictionary with audit statistics
        """
        stats = {
            "total_flagged": 0,
            "by_subreddit": {},
            "by_date": {},
            "avg_hallucination_score": 0.0,
            "avg_echo_score": 0.0,
        }

        total_hall_score = 0.0
        total_echo_score = 0.0

        # Read all log files
        for log_file in self.log_dir.glob("audit_*.jsonl"):
            with open(log_file, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        stats["total_flagged"] += 1

                        # By subreddit
                        subreddit = entry.get("subreddit", "unknown")
                        stats["by_subreddit"][subreddit] = (
                            stats["by_subreddit"].get(subreddit, 0) + 1
                        )

                        # By date
                        date = entry["timestamp"][:10]
                        stats["by_date"][date] = stats["by_date"].get(date, 0) + 1

                        # Scores
                        total_hall_score += entry.get("hallucination_score", 0)
                        total_echo_score += entry.get("echo_score", 0)

                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse log line in {log_file}")

        # Calculate averages
        if stats["total_flagged"] > 0:
            stats["avg_hallucination_score"] = total_hall_score / stats["total_flagged"]
            stats["avg_echo_score"] = total_echo_score / stats["total_flagged"]

        return stats

    def cleanup_old_logs(self, days: int = None) -> int:
        """
        Remove logs older than specified days

        Args:
            days: Number of days to retain (uses config.retention_days if not specified)

        Returns:
            Number of files deleted
        """
        retention_days = days or self.config.retention_days
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        deleted_count = 0

        for log_file in self.log_dir.glob("audit_*.jsonl"):
            # Extract date from filename
            try:
                date_str = log_file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=timezone.utc)

                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old log file: {log_file}")
            except (ValueError, IndexError):
                logger.warning(f"Could not parse date from log file: {log_file}")

        return deleted_count
