"""Audit PR template generator"""
import os
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AuditPRGenerator:
    """Generates audit_template.md files for flagged claims"""
    
    def __init__(self, output_dir: str = "audit_templates"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_prs(self, flagged_posts: List[Dict[str, Any]]) -> List[str]:
        """
        Generate audit PR templates for all flagged posts
        
        Args:
            flagged_posts: List of flagged post dictionaries
            
        Returns:
            List of generated file paths
        """
        generated_files = []
        
        for idx, flagged_post in enumerate(flagged_posts):
            filename = self._generate_pr_template(flagged_post, idx)
            generated_files.append(filename)
        
        return generated_files
    
    def _generate_pr_template(self, flagged_post: Dict[str, Any], index: int) -> str:
        """
        Generate a single audit PR template
        
        Args:
            flagged_post: Flagged post data
            index: Index number for filename
            
        Returns:
            Path to generated file
        """
        post = flagged_post['post']
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_template_{timestamp}_{index}.md"
        filepath = self.output_dir / filename
        
        # Build template content
        template = f"""# Audit Report: {post.get('title', 'Untitled')}

## Post Information
- **Post ID**: {post.get('id', 'N/A')}
- **Subreddit**: r/{post.get('subreddit', 'N/A')}
- **Author**: u/{post.get('author', 'N/A')}
- **URL**: {post.get('url', 'N/A')}
- **Created**: {post.get('created_utc', 'N/A')}

## Detection Results

### Hallucination Analysis
- **Score**: {flagged_post['hallucination_score']:.2f}
- **Flags Detected**: {len(flagged_post['hallucination_flags'])}

"""
        
        if flagged_post['hallucination_flags']:
            template += "**Specific Flags:**\n"
            for flag in flagged_post['hallucination_flags']:
                template += f"- {flag}\n"
            template += "\n"
        
        template += f"""### Echo Chain Analysis
- **Echo Score**: {flagged_post['echo_score']:.2f}
- **Echo Chains Found**: {len(flagged_post['echo_chains'])}

"""
        
        if flagged_post['echo_chains']:
            template += "**Echo Chain Details:**\n"
            for i, chain in enumerate(flagged_post['echo_chains'][:5], 1):  # Limit to 5
                template += f"{i}. Similar to post `{chain.get('id', 'unknown')}` "
                template += f"(similarity: {chain.get('similarity', 0):.2f})\n"
            template += "\n"
        
        template += """## Community Audit Checklist

Please review the flagged content and check the applicable items:

- [ ] **Confirmed Hallucination**: The post contains unverifiable claims about consciousness/sentience
- [ ] **Confirmed Echo Chain**: The post is part of a repetitive pattern
- [ ] **False Positive**: The detection is incorrect, post is legitimate
- [ ] **Needs Human Review**: Uncertain, requires expert evaluation

## Reviewer Comments

<!-- Add your observations here -->

## Verdict

- [ ] **Flag as problematic** - Action required
- [ ] **Clear as legitimate** - No action needed
- [ ] **Escalate for expert review**

---

**Audit Timestamp**: {flagged_post['timestamp']}
**Jules Version**: 0.1.0
**Detection Method**: Automated analysis with human verification required
"""
        
        # Write template file
        with open(filepath, 'w') as f:
            f.write(template)
        
        logger.info(f"Generated audit template: {filepath}")
        return str(filepath)
