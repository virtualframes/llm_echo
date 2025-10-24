#!/usr/bin/env python3
import argparse
import os
import re
import requests
from github import Github
from agents.jules.io_utils import sha256_hex_of_obj
from agents.provenance import emitevent
from search.deepseekadapter import deepseekquery
from agents.jules.qodo_reader import parse_qodo_comment_body

SCRAPEDO_URL = "https://api.scrape.do/render"
SCRAPEDO_API_KEY = "your-hardcoded-scrapedo-key"


def extract_url(text):
    match = re.search(r"https?://\S+", text)
    return match.group(0) if match else None


def fetch_html_via_scrapedo(url, api_key):
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    resp = requests.get(SCRAPEDO_URL, headers=headers, params={"url": url}, timeout=60)
    resp.raise_for_status()
    return resp.text


def scrape(args):
    html = fetch_html_via_scrapedo(args.url, SCRAPEDO_API_KEY)
    provenance_bundle = {"source": args.url, "claimid": args.claimid, "ingesttime": None}
    payload = deepseekquery(html, provenance_bundle=provenance_bundle)
    input_hash = sha256_hex_of_obj({"url": args.url, "claimid": args.claimid})
    if args.dry_run:
        print("DRY RUN payload:", payload)
        return
    event = emitevent(
        "jules_cli_scrape",
        "evidence_emitted",
        payload,
        commitsha=os.environ.get("GIT_COMMIT_SHA"),
        inputhash=input_hash,
    )
    print("Wrote event:", event["provenancetoken"])


def fetch_pr_comments(repo_full, pr_number, token):
    g = Github(token)
    repo = g.get_repo(repo_full)
    pr = repo.get_pull(pr_number)
    return [c for c in pr.get_issue_comments()]


def parse_qodo(args):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_PAT")
    comments = fetch_pr_comments(args.repo, args.pr, token)
    qodo_feedbacks = []
    for c in comments:
        if c.user and c.user.login and "qodo" in c.user.login.lower():
            parsed = parse_qodo_comment_body(c.body or "")
            qodo_feedbacks.append({"author": c.user.login, "parsed": parsed, "id": c.id})
    payload = {"qodofeedback": qodo_feedbacks, "pr": args.pr, "repo": args.repo}
    input_hash = sha256_hex_of_obj({"repo": args.repo, "pr": args.pr})
    if args.dry_run:
        print("DRY RUN qodo payload:", payload)
        return
    event = emitevent(
        "jules_cli_parse_qodo",
        "qodo_feedback",
        payload,
        commitsha=os.environ.get("GIT_COMMIT_SHA"),
        inputhash=input_hash,
    )
    print("Wrote event:", event["provenancetoken"])


def dispatch(args):
    comment_body = args.comment
    if "/deepseek-scan" in comment_body:
        url = extract_url(comment_body)
        if url:
            claim_id = os.environ.get("GITHUB_ISSUE_NUMBER", "unknown")
            scrape_args = argparse.Namespace(url=url, claimid=claim_id, dry_run=args.dry_run)
            scrape(scrape_args)
        else:
            print("No URL found in comment.")
    elif "/qodo-feedback" in comment_body or "@jules parse qodo" in comment_body:
        repo = os.environ.get("GITHUB_REPOSITORY", "unknown")
        pr_number = int(os.environ.get("GITHUB_ISSUE_NUMBER", 0))
        if pr_number:
            parse_qodo_args = argparse.Namespace(repo=repo, pr=pr_number, dry_run=args.dry_run)
            parse_qodo(parse_qodo_args)
        else:
            print("Could not determine PR number.")
    else:
        print("No known command found in comment.")


def main():
    parser = argparse.ArgumentParser(description="Jules Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Scrape subcommand
    parser_scrape = subparsers.add_parser(
        "scrape", help="Scrape a URL and emit a provenance event."
    )
    parser_scrape.add_argument("--url", required=True)
    parser_scrape.add_argument("--claimid", required=True)
    parser_scrape.add_argument("--dry-run", action="store_true")
    parser_scrape.set_defaults(func=scrape)

    # Parse Qodo subcommand
    parser_parse_qodo = subparsers.add_parser(
        "parse-qodo", help="Parse Qodo comments from a PR and emit a provenance event."
    )
    parser_parse_qodo.add_argument("--repo", required=True)
    parser_parse_qodo.add_argument("--pr", required=True, type=int)
    parser_parse_qodo.add_argument("--dry-run", action="store_true")
    parser_parse_qodo.set_defaults(func=parse_qodo)

    # Dispatch subcommand
    parser_dispatch = subparsers.add_parser(
        "dispatch", help="Dispatch a command from a comment body."
    )
    parser_dispatch.add_argument("--comment", required=True)
    parser_dispatch.add_argument("--dry-run", action="store_true")
    parser_dispatch.set_defaults(func=dispatch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
