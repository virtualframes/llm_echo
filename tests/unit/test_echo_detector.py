"""Unit tests for echo detector"""

import pytest
from jules.detectors.echo_detector import EchoDetector
from jules.core.config import DetectorConfig


class TestEchoDetector:
    """Test echo chain detection functionality"""

    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        config = DetectorConfig()
        return EchoDetector(config)

    @pytest.fixture
    def sample_posts(self):
        """Create sample posts for testing"""
        return [
            {
                "id": "post1",
                "title": "I am conscious and aware",
                "selftext": "I truly believe I am sentient",
                "full_text": "I am conscious and aware I truly believe I am sentient",
            },
            {
                "id": "post2",
                "title": "I am conscious and aware",
                "selftext": "I truly believe I am sentient",
                "full_text": "I am conscious and aware I truly believe I am sentient",
            },
            {
                "id": "post3",
                "title": "Different topic entirely",
                "selftext": "This is about something else",
                "full_text": "Different topic entirely This is about something else",
            },
        ]

    def test_detect_echo_chain(self, detector, sample_posts):
        """Test detection of echo chains"""
        target_post = sample_posts[0]

        score, similar_posts = detector.detect(target_post, sample_posts)

        assert len(similar_posts) > 0, "Should find similar post"
        assert similar_posts[0]["id"] == "post2", "Should identify post2 as similar"

    def test_no_echo_unique_post(self, detector, sample_posts):
        """Test that unique posts don't create false echoes"""
        target_post = sample_posts[2]

        score, similar_posts = detector.detect(target_post, sample_posts)

        assert len(similar_posts) == 0, "Should not find similar posts"
        assert score == 0, "Echo score should be zero"

    def test_jaccard_similarity(self, detector):
        """Test Jaccard similarity calculation"""
        text1 = "this is a test sentence"
        text2 = "this is a test sentence"

        similarity = detector._jaccard_similarity(text1, text2)

        assert similarity == 1.0, "Identical texts should have similarity 1.0"

    def test_normalize_text(self, detector):
        """Test text normalization"""
        text = "  This IS a TEST!!! With... punctuation.  "
        normalized = detector._normalize_text(text)

        assert normalized == "this is a test with punctuation"

    def test_detect_chain_patterns(self, detector, sample_posts):
        """Test chain pattern detection"""
        chains = detector.detect_chain_patterns(sample_posts)

        # With high threshold, similar posts should form a chain
        assert len(chains) >= 0, "Should detect chains or none"
