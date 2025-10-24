"""Echo detector for identifying repetitive content chains"""
import logging
from typing import Dict, Any, List, Tuple
from collections import Counter
import re

logger = logging.getLogger(__name__)


class EchoDetector:
    """Detects echo chains - repetitive patterns across posts"""
    
    def __init__(self, config):
        self.config = config
        self.threshold = config.echo_threshold
        self.min_chain_length = config.min_echo_chain_length
        self.similarity_method = config.similarity_method
    
    def detect(self, post: Dict[str, Any], all_posts: List[Dict[str, Any]]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Detect echo chains for a given post
        
        Args:
            post: Target post to analyze
            all_posts: All posts to compare against
            
        Returns:
            Tuple of (echo_score, list of similar posts)
        """
        similar_posts = []
        
        post_text = self._normalize_text(
            post.get('full_text', '') or f"{post.get('title', '')} {post.get('selftext', '')}"
        )
        
        for other_post in all_posts:
            # Skip self-comparison
            if other_post.get('id') == post.get('id'):
                continue
            
            other_text = self._normalize_text(
                other_post.get('full_text', '') or f"{other_post.get('title', '')} {other_post.get('selftext', '')}"
            )
            
            # Calculate similarity
            similarity = self._calculate_similarity(post_text, other_text)
            
            if similarity >= self.threshold:
                similar_posts.append({
                    'id': other_post.get('id'),
                    'title': other_post.get('title'),
                    'similarity': similarity,
                    'subreddit': other_post.get('subreddit'),
                    'author': other_post.get('author')
                })
        
        # Calculate echo score based on number of similar posts
        echo_score = min(len(similar_posts) / 5.0, 1.0)
        
        return echo_score, similar_posts
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        if self.similarity_method == "jaccard":
            return self._jaccard_similarity(text1, text2)
        elif self.similarity_method == "cosine":
            return self._cosine_similarity(text1, text2)
        else:
            return self._jaccard_similarity(text1, text2)
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity (simplified bag-of-words version)"""
        words1 = text1.split()
        words2 = text2.split()
        
        # Create word frequency vectors
        all_words = set(words1 + words2)
        vec1 = [words1.count(word) for word in all_words]
        vec2 = [words2.count(word) for word in all_words]
        
        # Calculate dot product and magnitudes
        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
        mag1 = sum(v1 ** 2 for v1 in vec1) ** 0.5
        mag2 = sum(v2 ** 2 for v2 in vec2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def detect_chain_patterns(self, all_posts: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Detect chains of similar posts
        
        Args:
            all_posts: All posts to analyze
            
        Returns:
            List of chains (each chain is a list of post IDs)
        """
        chains = []
        processed = set()
        
        for post in all_posts:
            post_id = post.get('id')
            
            if post_id in processed:
                continue
            
            # Find all similar posts
            _, similar_posts = self.detect(post, all_posts)
            
            if len(similar_posts) >= self.min_chain_length - 1:
                chain = [post_id] + [p['id'] for p in similar_posts]
                chains.append(chain)
                processed.update(chain)
        
        return chains
