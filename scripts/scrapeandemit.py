#!/usr/bin/env python3
import argparse
import os
import requests
from agents.jules.io_utils import sha256_hex_of_obj
from agents.provenance import emitevent
from search.deepseekadapter import deepseekquery

SCRAPEDO_URL = os.environ.get("SCRAPEDO_URL", "https://api.scrape.do/render")


def fetch_html_via_scrapedo(url, api_key):
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    resp = requests.get(SCRAPEDO_URL, headers=headers, params={"url": url}, timeout=60)
    resp.raise_for_status()
    return resp.text


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--claimid", required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    api_key = os.environ.get("SCRAPEDO_API_KEY")
    html = fetch_html_via_scrapedo(args.url, api_key)
    provenance_bundle = {"source": args.url, "claimid": args.claimid, "ingesttime": None}
    payload = deepseekquery(html, provenance_bundle=provenance_bundle)
    # compute inputhash for provenance (sha256 of url+claimid)
    input_hash = sha256_hex_of_obj({"url": args.url, "claimid": args.claimid})
    if args.dry_run:
        print("DRY RUN payload:", payload)
        return
    event = emitevent(
        "scrapeandemit",
        payload,
        commitsha=os.environ.get("GIT_COMMIT_SHA"),
        inputhash=input_hash,
    )
    print("Wrote event:", event["provenancetoken"])


if __name__ == "__main__":
    main()
