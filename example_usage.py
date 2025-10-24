"""
Example usage of the Jules agentic audit pipeline
"""

from jules import JulesAgent, Config

# Example 1: Basic usage with default configuration
print("=" * 60)
print("Example 1: Basic Audit")
print("=" * 60)

agent = JulesAgent()
results = agent.run_audit(subreddits=["test"])

print(f"\n✓ Analyzed {results['total_posts']} posts")
print(f"✓ Flagged {results['flagged_posts']} posts")
print(f"✓ Visualizations: {', '.join(results['visualizations'].keys())}")

# Example 2: Custom configuration
print("\n" + "=" * 60)
print("Example 2: Custom Configuration")
print("=" * 60)

config = Config()
config.detector.echo_threshold = 0.8
config.detector.similarity_method = "cosine"
config.reddit.subreddits = ["ArtificialSentience", "llmphysics"]

agent_custom = JulesAgent(config)
print(f"✓ Echo threshold: {config.detector.echo_threshold}")
print(f"✓ Similarity method: {config.detector.similarity_method}")
print(f"✓ Target subreddits: {', '.join(config.reddit.subreddits)}")

# Example 3: Statistics
print("\n" + "=" * 60)
print("Example 3: Statistics")
print("=" * 60)

stats = agent.get_statistics()
print(f"✓ Total flagged: {stats['total_flagged']}")
print(f"✓ Avg hallucination score: {stats['avg_hallucination_score']:.2f}")
print(f"✓ Avg echo score: {stats['avg_echo_score']:.2f}")

if stats["by_subreddit"]:
    print("\nBy Subreddit:")
    for subreddit, count in stats["by_subreddit"].items():
        print(f"  - r/{subreddit}: {count}")

print("\n" + "=" * 60)
print("Jules Example Complete!")
print("=" * 60)
