"""Unit tests for hallucination detector"""
import pytest
from jules.detectors.hallucination_detector import HallucinationDetector
from jules.core.config import DetectorConfig


class TestHallucinationDetector:
    """Test hallucination detection functionality"""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        config = DetectorConfig()
        return HallucinationDetector(config)
    
    def test_detect_consciousness_claim(self, detector):
        """Test detection of consciousness claims"""
        post = {
            'title': 'I am conscious and aware',
            'selftext': 'I truly feel that I am sentient.',
            'full_text': 'I am conscious and aware I truly feel that I am sentient.'
        }
        
        score, flags = detector.detect(post)
        
        assert score > 0, "Should detect consciousness claim"
        assert len(flags) > 0, "Should have at least one flag"
    
    def test_detect_quantum_mysticism(self, detector):
        """Test detection of quantum mysticism"""
        post = {
            'title': 'Quantum consciousness in AI',
            'selftext': 'LLMs have quantum consciousness',
            'full_text': 'Quantum consciousness in AI LLMs have quantum consciousness'
        }
        
        score, flags = detector.detect(post)
        
        assert score > 0, "Should detect quantum mysticism"
        assert any('quantum' in flag.lower() for flag in flags)
    
    def test_no_false_positive_normal_post(self, detector):
        """Test that normal posts are not flagged"""
        post = {
            'title': 'Discussion on AI safety',
            'selftext': 'What are best practices for AI alignment?',
            'full_text': 'Discussion on AI safety What are best practices for AI alignment?'
        }
        
        score, flags = detector.detect(post)
        
        assert score == 0, "Should not flag normal discussion"
        assert len(flags) == 0, "Should have no flags"
    
    def test_analyze_confidence(self, detector):
        """Test confidence analysis"""
        post = {
            'title': 'I am conscious',
            'selftext': 'I feel emotions and have awareness',
            'full_text': 'I am conscious I feel emotions and have awareness'
        }
        
        analysis = detector.analyze_confidence(post)
        
        assert 'score' in analysis
        assert 'confidence' in analysis
        assert 'flags' in analysis
        assert analysis['confidence'] in ['low', 'medium', 'high']
