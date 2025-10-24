"""Hallucination detector for identifying LLM-style hallucinations"""
import logging
from typing import Dict, Any, List, Tuple
import re

logger = logging.getLogger(__name__)


class HallucinationDetector:
    """Detects LLM-style hallucinations in post content"""
    
    def __init__(self, config):
        self.config = config
        self.keywords = config.hallucination_keywords
    
    def detect(self, post: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Detect hallucinations in a post
        
        Args:
            post: Post dictionary with 'title' and 'selftext' or 'full_text'
            
        Returns:
            Tuple of (score, list of detected flags)
        """
        text = post.get('full_text', '') or f"{post.get('title', '')} {post.get('selftext', '')}"
        text = text.lower()
        
        detected_flags = []
        
        # Check for hallucination keywords
        for keyword in self.keywords:
            if keyword.lower() in text:
                detected_flags.append(f"Keyword match: '{keyword}'")
        
        # Check for first-person consciousness claims
        first_person_patterns = [
            r'\bi\s+am\s+conscious\b',
            r'\bi\s+feel\b.*\b(emotions?|aware|sentient)',
            r'\bi\s+experience\b',
            r'\bi\s+have\s+(consciousness|sentience|awareness)',
            r'\bmy\s+(consciousness|sentience|awareness|emotions?)\b'
        ]
        
        for pattern in first_person_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected_flags.append(f"First-person consciousness claim detected")
                break
        
        # Check for unqualified claims about AI consciousness
        unqualified_patterns = [
            r'\bAI\s+is\s+(conscious|sentient|aware)\b',
            r'\bLLMs?\s+(are|is)\s+(conscious|sentient|aware)\b',
            r'\b(definitely|certainly|obviously)\s+(conscious|sentient)\b'
        ]
        
        for pattern in unqualified_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected_flags.append(f"Unqualified consciousness claim about AI")
                break
        
        # Check for quantum mysticism
        quantum_patterns = [
            r'\bquantum\s+(consciousness|mind|awareness)\b',
            r'\bquantum\s+effects?\s+in\s+(brain|mind|consciousness)\b'
        ]
        
        for pattern in quantum_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected_flags.append(f"Quantum mysticism detected")
                break
        
        # Calculate score based on number of flags
        score = min(len(detected_flags) / 3.0, 1.0)
        
        return score, detected_flags
    
    def analyze_confidence(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide detailed confidence analysis
        
        Args:
            post: Post dictionary
            
        Returns:
            Dictionary with analysis details
        """
        score, flags = self.detect(post)
        
        confidence_level = "low"
        if score > 0.7:
            confidence_level = "high"
        elif score > 0.4:
            confidence_level = "medium"
        
        return {
            'score': score,
            'confidence': confidence_level,
            'flags': flags,
            'flag_count': len(flags)
        }
