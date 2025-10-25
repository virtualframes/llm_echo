import re


def apply_heuristics(text: str) -> list:
    """
    Applies rule-based heuristics to identify potential claims.
    Returns a list of dictionaries, where each dictionary represents a potential claim.
    """
    claims = []

    # Example heuristic: look for sentences containing "I think that..."
    for match in re.finditer(r"I think that.*?\.", text, re.IGNORECASE):
        claims.append({"text": match.group(0), "span": match.span(), "source": "heuristic_I_think"})

    return claims


def main():
    sample_text = "This is a post. I think that this is a claim. What do you think?"
    detected_claims = apply_heuristics(sample_text)
    print("Detected claims:")
    for claim in detected_claims:
        print(f"- Text: '{claim['text']}' (Span: {claim['span']}), Source: {claim['source']}")


if __name__ == "__main__":
    main()
