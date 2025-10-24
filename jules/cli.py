"""Command-line interface for Jules"""
import argparse
import logging
import sys
from pathlib import Path

from jules import JulesAgent, Config


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Jules: Agentic Audit Pipeline for LLM Echo Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run audit with default settings
  jules audit
  
  # Run audit with specific subreddits
  jules audit -s ArtificialSentience llmphysics
  
  # Use custom configuration
  jules audit --config config.yaml
  
  # Show statistics
  jules stats
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Audit command
    audit_parser = subparsers.add_parser('audit', help='Run audit pipeline')
    audit_parser.add_argument('-s', '--subreddits', nargs='+',
                             help='Subreddits to audit (overrides config)')
    audit_parser.add_argument('-c', '--config', type=str,
                             help='Path to configuration YAML file')
    audit_parser.add_argument('--no-viz', action='store_true',
                             help='Skip visualization generation')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show audit statistics')
    stats_parser.add_argument('-c', '--config', type=str,
                             help='Path to configuration YAML file')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean old logs')
    cleanup_parser.add_argument('-d', '--days', type=int, default=90,
                               help='Keep logs from last N days (default: 90)')
    cleanup_parser.add_argument('-c', '--config', type=str,
                               help='Path to configuration YAML file')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    if hasattr(args, 'config') and args.config:
        config = Config.from_yaml(args.config)
        logger.info(f"Loaded configuration from {args.config}")
    else:
        config = Config()
        logger.info("Using default configuration")
    
    # Execute command
    if args.command == 'audit':
        logger.info("Starting audit pipeline...")
        agent = JulesAgent(config)
        
        subreddits = args.subreddits if args.subreddits else None
        results = agent.run_audit(subreddits)
        
        # Print summary
        print("\n" + "="*60)
        print("AUDIT SUMMARY")
        print("="*60)
        print(f"Total posts analyzed: {results['total_posts']}")
        print(f"Flagged posts: {results['flagged_posts']}")
        print(f"Subreddits: {', '.join(results['subreddits'])}")
        print(f"Timestamp: {results['timestamp']}")
        
        if results.get('visualizations'):
            print("\nVisualizations created:")
            for name, path in results['visualizations'].items():
                print(f"  - {name}: {path}")
        
        print("\nAudit templates generated in: audit_templates/")
        print("Provenance logs saved in: provenance_logs/")
        print("="*60 + "\n")
        
    elif args.command == 'stats':
        logger.info("Retrieving statistics...")
        agent = JulesAgent(config)
        stats = agent.get_statistics()
        
        print("\n" + "="*60)
        print("AUDIT STATISTICS")
        print("="*60)
        print(f"Total flagged posts: {stats['total_flagged']}")
        print(f"Average hallucination score: {stats['avg_hallucination_score']:.2f}")
        print(f"Average echo score: {stats['avg_echo_score']:.2f}")
        
        if stats['by_subreddit']:
            print("\nBy Subreddit:")
            for sr, count in stats['by_subreddit'].items():
                print(f"  r/{sr}: {count}")
        
        if stats['by_date']:
            print("\nBy Date:")
            for date, count in sorted(stats['by_date'].items())[-10:]:
                print(f"  {date}: {count}")
        
        print("="*60 + "\n")
        
    elif args.command == 'cleanup':
        logger.info(f"Cleaning logs older than {args.days} days...")
        agent = JulesAgent(config)
        deleted = agent.provenance_logger.cleanup_old_logs(args.days)
        print(f"\nDeleted {deleted} old log file(s)")
        
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
