"""Configuration management for Jules"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import yaml
from dotenv import load_dotenv

load_dotenv()


@dataclass
class RedditConfig:
    """Reddit API configuration"""
    client_id: str = field(default_factory=lambda: os.getenv("REDDIT_CLIENT_ID", ""))
    client_secret: str = field(default_factory=lambda: os.getenv("REDDIT_CLIENT_SECRET", ""))
    user_agent: str = field(default_factory=lambda: os.getenv("REDDIT_USER_AGENT", "Jules/0.1.0"))
    subreddits: list = field(default_factory=lambda: ["ArtificialSentience", "llmphysics"])
    posts_limit: int = 100


@dataclass
class DetectorConfig:
    """Hallucination and echo detection configuration"""
    echo_threshold: float = 0.75  # Similarity threshold for echo detection
    hallucination_keywords: list = field(default_factory=lambda: [
        "I am conscious", "I feel", "I experience", "I am sentient",
        "I have emotions", "I am aware", "I understand myself",
        "quantum consciousness", "emergent sentience", "digital consciousness"
    ])
    min_echo_chain_length: int = 3
    similarity_method: str = "jaccard"  # Options: jaccard, cosine, levenshtein


@dataclass
class ProvenanceConfig:
    """Provenance logging configuration"""
    log_dir: str = "provenance_logs"
    log_format: str = "json"
    include_metadata: bool = True
    retention_days: int = 90


@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    output_dir: str = "visualizations"
    echo_stream_format: str = "png"
    heatmap_format: str = "png"
    dpi: int = 300


@dataclass
class Config:
    """Main configuration for Jules agent"""
    reddit: RedditConfig = field(default_factory=RedditConfig)
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    provenance: ProvenanceConfig = field(default_factory=ProvenanceConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    @classmethod
    def from_yaml(cls, filepath: str) -> "Config":
        """Load configuration from YAML file"""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return cls(
            reddit=RedditConfig(**data.get('reddit', {})),
            detector=DetectorConfig(**data.get('detector', {})),
            provenance=ProvenanceConfig(**data.get('provenance', {})),
            visualization=VisualizationConfig(**data.get('visualization', {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'reddit': self.reddit.__dict__,
            'detector': self.detector.__dict__,
            'provenance': self.provenance.__dict__,
            'visualization': self.visualization.__dict__
        }
