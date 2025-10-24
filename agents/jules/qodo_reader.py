from typing import Dict, Any, List
import re


def extract_json_blocks(text: str) -> List[str]:
    # naive JSON code block matcher
    return re.findall(r"```json\n(.*?)\n```", text, flags=re.S)


def parse_qodo_comment_body(body: str) -> Dict[str, Any]:
    """
    Parse common Qodo reply shapes into structured feedback.
    Returns a dict with summary, risks, ci_failures, recommendations.
    """
    feedback = {
        "summary": "",
        "risks": [],
        "ci_failures": [],
        "recommendations": [],
    }
    # Summary: first paragraph
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    if paragraphs:
        feedback["summary"] = paragraphs[0]
    # Extract code-block JSON if present
    json_blocks = extract_json_blocks(body)
    if json_blocks:
        feedback["parsed_json_blocks"] = json_blocks
    # Simple heuristics for lists
    for line in body.splitlines():
        l = line.strip()
        if l.startswith("- Risk:") or "risk" in l.lower():
            feedback["risks"].append(l)
        if "ci failure" in l.lower() or "failing" in l.lower():
            feedback["ci_failures"].append(l)
        if l.startswith("- Recommend") or l.startswith("- Suggest"):
            feedback["recommendations"].append(l)
    return feedback
