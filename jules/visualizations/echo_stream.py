"""Echo stream visualization"""

import logging
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("matplotlib not available, visualizations will be skipped")

logger = logging.getLogger(__name__)


class EchoStreamVisualizer:
    """Creates echo stream visualizations showing temporal patterns"""

    def __init__(self, config):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create(self, flagged_posts: List[Dict[str, Any]], all_posts: List[Dict[str, Any]]) -> str:
        """
        Create echo stream visualization

        Args:
            flagged_posts: List of flagged posts with detection results
            all_posts: All posts for context

        Returns:
            Path to generated visualization file
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Cannot create visualization: matplotlib not available")
            return ""

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"echo_stream_{timestamp}.{self.config.echo_stream_format}"
        filepath = self.output_dir / filename

        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle("Echo Stream Analysis", fontsize=16, fontweight="bold")

        # Extract data
        post_times = []
        echo_scores = []
        hallucination_scores = []

        for fp in flagged_posts:
            try:
                # Try to parse timestamp
                timestamp_str = fp["post"].get("created_utc", "")
                if timestamp_str:
                    if isinstance(timestamp_str, str):
                        post_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    else:
                        post_time = datetime.fromtimestamp(timestamp_str)
                    post_times.append(post_time)
                    echo_scores.append(fp["echo_score"])
                    hallucination_scores.append(fp["hallucination_score"])
            except (ValueError, TypeError) as e:
                logger.debug(f"Could not parse timestamp: {e}")
                continue

        if post_times:
            # Plot 1: Echo scores over time
            ax1.plot(
                post_times,
                echo_scores,
                "o-",
                color="#e74c3c",
                linewidth=2,
                markersize=6,
                label="Echo Score",
            )
            ax1.set_ylabel("Echo Score", fontsize=12)
            ax1.set_title("Echo Detection Over Time", fontsize=14)
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            ax1.set_ylim(-0.1, 1.1)

            # Plot 2: Hallucination scores over time
            ax2.plot(
                post_times,
                hallucination_scores,
                "s-",
                color="#3498db",
                linewidth=2,
                markersize=6,
                label="Hallucination Score",
            )
            ax2.set_xlabel("Time", fontsize=12)
            ax2.set_ylabel("Hallucination Score", fontsize=12)
            ax2.set_title("Hallucination Detection Over Time", fontsize=14)
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            ax2.set_ylim(-0.1, 1.1)

            # Format x-axis
            for ax in [ax1, ax2]:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
        else:
            # No data to plot
            ax1.text(0.5, 0.5, "No temporal data available", ha="center", va="center", fontsize=14)
            ax2.text(0.5, 0.5, "No temporal data available", ha="center", va="center", fontsize=14)

        plt.tight_layout()
        plt.savefig(filepath, dpi=self.config.dpi, bbox_inches="tight")
        plt.close()

        logger.info(f"Created echo stream visualization: {filepath}")
        return str(filepath)
