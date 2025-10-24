"""Unit tests for configuration"""
import pytest
import yaml
from pathlib import Path
from jules.core.config import Config, RedditConfig, DetectorConfig


class TestConfig:
    """Test configuration management"""
    
    def test_default_config(self):
        """Test default configuration creation"""
        config = Config()
        
        assert config.reddit is not None
        assert config.detector is not None
        assert config.provenance is not None
        assert config.visualization is not None
    
    def test_reddit_config_defaults(self):
        """Test Reddit configuration defaults"""
        reddit_config = RedditConfig()
        
        assert reddit_config.subreddits == ["ArtificialSentience", "llmphysics"]
        assert reddit_config.posts_limit == 100
    
    def test_detector_config_defaults(self):
        """Test detector configuration defaults"""
        detector_config = DetectorConfig()
        
        assert detector_config.echo_threshold == 0.75
        assert detector_config.min_echo_chain_length == 3
        assert detector_config.similarity_method == "jaccard"
    
    def test_config_to_dict(self):
        """Test configuration conversion to dictionary"""
        config = Config()
        config_dict = config.to_dict()
        
        assert 'reddit' in config_dict
        assert 'detector' in config_dict
        assert 'provenance' in config_dict
        assert 'visualization' in config_dict
    
    def test_config_from_yaml(self, tmp_path):
        """Test loading configuration from YAML"""
        # Create temporary YAML file
        yaml_content = {
            'reddit': {
                'subreddits': ['test1', 'test2'],
                'posts_limit': 50
            },
            'detector': {
                'echo_threshold': 0.8,
                'similarity_method': 'cosine'
            }
        }
        
        yaml_file = tmp_path / "test_config.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)
        
        # Load config
        config = Config.from_yaml(str(yaml_file))
        
        assert config.reddit.subreddits == ['test1', 'test2']
        assert config.reddit.posts_limit == 50
        assert config.detector.echo_threshold == 0.8
        assert config.detector.similarity_method == 'cosine'
