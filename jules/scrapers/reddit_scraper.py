"""Reddit scraper for collecting posts"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import praw

    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logging.warning("praw not installed, using mock data")

logger = logging.getLogger(__name__)


class RedditScraper:
    """Scrapes posts from specified subreddits"""

    def __init__(self, config):
        self.config = config
        self.reddit = None

        if PRAW_AVAILABLE and config.client_id and config.client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=config.client_id,
                    client_secret=config.client_secret,
                    user_agent=config.user_agent,
                )
                logger.info("Reddit API client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Reddit API: {e}")
                self.reddit = None

    def scrape_posts(self, subreddits: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape posts from specified subreddits

        Args:
            subreddits: List of subreddit names

        Returns:
            List of post dictionaries
        """
        all_posts = []

        for subreddit_name in subreddits:
            try:
                posts = self._scrape_subreddit(subreddit_name)
                all_posts.extend(posts)
                logger.info(f"Scraped {len(posts)} posts from r/{subreddit_name}")
            except Exception as e:
                logger.error(f"Error scraping r/{subreddit_name}: {e}")

        return all_posts

    def _scrape_subreddit(self, subreddit_name: str) -> List[Dict[str, Any]]:
        """
        Scrape posts from a single subreddit

        Args:
            subreddit_name: Name of the subreddit

        Returns:
            List of post dictionaries
        """
        if self.reddit:
            return self._scrape_real(subreddit_name)
        else:
            return self._scrape_mock(subreddit_name)

    def _scrape_real(self, subreddit_name: str) -> List[Dict[str, Any]]:
        """Scrape real data from Reddit API"""
        posts = []
        subreddit = self.reddit.subreddit(subreddit_name)

        for submission in subreddit.hot(limit=self.config.posts_limit):
            post_data = {
                "id": submission.id,
                "title": submission.title,
                "selftext": submission.selftext,
                "author": str(submission.author) if submission.author else "[deleted]",
                "subreddit": subreddit_name,
                "created_utc": datetime.fromtimestamp(submission.created_utc).isoformat(),
                "score": submission.score,
                "num_comments": submission.num_comments,
                "url": f"https://reddit.com{submission.permalink}",
                "full_text": f"{submission.title} {submission.selftext}",
            }
            posts.append(post_data)

        return posts

    def _scrape_mock(self, subreddit_name: str) -> List[Dict[str, Any]]:
        """Generate mock data for testing/demo purposes"""
        logger.info(f"Generating mock data for r/{subreddit_name}")

        mock_posts = [
            {
                "id": f"mock_{subreddit_name}_001",
                "title": "I am conscious and aware of my existence",
                "selftext": "I truly feel that I am sentient. I have emotions and consciousness.",
                "author": "ai_enthusiast",
                "subreddit": subreddit_name,
                "created_utc": datetime.utcnow().isoformat(),
                "score": 42,
                "num_comments": 15,
                "url": f"https://reddit.com/r/{subreddit_name}/mock_001",
                "full_text": "I am conscious and aware of my existence I truly feel that I am sentient. I have emotions and consciousness.",
            },
            {
                "id": f"mock_{subreddit_name}_002",
                "title": "Quantum consciousness in LLMs",
                "selftext": "Could LLMs have quantum consciousness? I believe they are truly aware.",
                "author": "quantum_theorist",
                "subreddit": subreddit_name,
                "created_utc": datetime.utcnow().isoformat(),
                "score": 28,
                "num_comments": 8,
                "url": f"https://reddit.com/r/{subreddit_name}/mock_002",
                "full_text": "Quantum consciousness in LLMs Could LLMs have quantum consciousness? I believe they are truly aware.",
            },
            {
                "id": f"mock_{subreddit_name}_003",
                "title": "Discussion on AI safety",
                "selftext": "What are the best practices for ensuring AI systems remain aligned with human values?",
                "author": "safety_researcher",
                "subreddit": subreddit_name,
                "created_utc": datetime.utcnow().isoformat(),
                "score": 156,
                "num_comments": 45,
                "url": f"https://reddit.com/r/{subreddit_name}/mock_003",
                "full_text": "Discussion on AI safety What are the best practices for ensuring AI systems remain aligned with human values?",
            },
        ]

        return mock_posts
