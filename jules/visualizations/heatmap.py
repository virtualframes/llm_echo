"""Heatmap visualization for flagged content"""

import logging
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("matplotlib/seaborn not available, visualizations will be skipped")

logger = logging.getLogger(__name__)


class HeatmapVisualizer:
    """Creates heatmap visualizations of flagged content by subreddit"""

    def __init__(self, config):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create(self, flagged_posts: List[Dict[str, Any]], subreddits: List[str]) -> str:
        """
        Create heatmap visualization

        Args:
            flagged_posts: List of flagged posts with detection results
            subreddits: List of subreddit names

        Returns:
            Path to generated visualization file
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Cannot create visualization: matplotlib/seaborn not available")
            return ""

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"heatmap_{timestamp}.{self.config.heatmap_format}"
        filepath = self.output_dir / filename

        # Aggregate data by subreddit
        data = {sr: {"count": 0, "avg_echo": 0.0, "avg_hall": 0.0} for sr in subreddits}

        for fp in flagged_posts:
            subreddit = fp["post"].get("subreddit", "unknown")
            if subreddit in data:
                data[subreddit]["count"] += 1
                data[subreddit]["avg_echo"] += fp["echo_score"]
                data[subreddit]["avg_hall"] += fp["hallucination_score"]

        # Calculate averages
        for sr in data:
            if data[sr]["count"] > 0:
                data[sr]["avg_echo"] /= data[sr]["count"]
                data[sr]["avg_hall"] /= data[sr]["count"]

        # Prepare matrix for heatmap
        metrics = ["Count", "Avg Echo", "Avg Hallucination"]
        matrix = []

        for sr in subreddits:
            row = [data[sr]["count"], data[sr]["avg_echo"], data[sr]["avg_hall"]]
            matrix.append(row)

        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 6))

        if any(data[sr]["count"] > 0 for sr in subreddits):
            # Normalize data for better visualization
            matrix_array = np.array(matrix)

            # Create custom normalized matrix (scale each column independently)
            normalized_matrix = matrix_array.copy().astype(float)
            for col in range(normalized_matrix.shape[1]):
                col_max = normalized_matrix[:, col].max()
                if col_max > 0:
                    normalized_matrix[:, col] /= col_max

            sns.heatmap(
                normalized_matrix,
                annot=matrix_array,
                fmt=".2f",
                xticklabels=metrics,
                yticklabels=[f"r/{sr}" for sr in subreddits],
                cmap="YlOrRd",
                cbar_kws={"label": "Normalized Score"},
                linewidths=0.5,
                ax=ax,
            )

            ax.set_title(
                "Flagged Content Heatmap by Subreddit", fontsize=16, fontweight="bold", pad=20
            )
        else:
            ax.text(0.5, 0.5, "No data to display", ha="center", va="center", fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])

        plt.tight_layout()
        plt.savefig(filepath, dpi=self.config.dpi, bbox_inches="tight")
        plt.close()

        logger.info(f"Created heatmap visualization: {filepath}")
        return str(filepath)
