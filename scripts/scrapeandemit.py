import argparse
import json
import os
from datetime import datetime, timezone
import requests
from search.deepseekadapter import deepseekquery
from agents.provenance import emitevent

def scrape_and_emit(url: str, dry_run: bool):
    """
    Scrapes a URL, processes it with DeepSeek, and emits a provenance event.
    """
    # Scrape.do API call
    scrape_do_api_key = os.environ.get("SCRAPEDO_API_KEY")
    if not scrape_do_api_key:
        raise ValueError("SCRAPEDO_API_KEY environment variable not set")

    scrape_do_url = f"http://api.scrape.do?token={scrape_do_api_key}&url={url}"
    response = requests.get(scrape_do_url)
    response.raise_for_status()
    html_content = response.text

    # DeepSeek query
    deepseek_query_obj = {
        "model": "deepseek-coder",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract key information from this HTML: {html_content}"}
        ]
    }

    provenance_bundle = {
        "source": url,
        "claimid": "some_claim_id",
        "ingesttime": datetime.now(timezone.utc).isoformat()
    }

    if not dry_run:
        evidence = deepseekquery(deepseek_query_obj, provenance_bundle)
        emitevent(
            module="scrapeandemit",
            eventtype="scrape_and_emit_complete",
            payload={"url": url, "status": "success", "evidence_count": len(evidence)}
        )
    else:
        print("---DRY RUN---")
        print("Would call DeepSeek adapter which would generate a 'deepseek_api_call' event.")
        print("Would also generate a 'scrape_and_emit_complete' event with the following payload:")
        print(json.dumps({
            "url": url,
            "status": "success",
            "evidence_count": "N/A"
        }, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape a URL and emit a provenance event.")
    parser.add_argument("url", type=str, help="The URL to scrape.")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without emitting events.")
    args = parser.parse_args()

    scrape_and_emit(args.url, args.dry_run)
