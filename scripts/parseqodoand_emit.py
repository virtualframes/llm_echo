#!/usr/bin/env python3
import argparse
import os
from github import Github
from agents.jules.qodo_reader import parse_qodo_comment_body
from agents.provenance import emitevent
from agents.jules.io_utils import sha256_hex_of_obj


def fetch_pr_comments(repo_full, pr_number, token):
    g = Github(token)
    repo = g.get_repo(repo_full)
    pr = repo.get_pull(pr_number)
    return [c for c in pr.get_issue_comments()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--pr", required=True, type=int)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_PAT")
    comments = fetch_pr_comments(args.repo, args.pr, token)
    qodo_feedbacks = []
    for c in comments:
        if c.user and c.user.login and "qodo" in c.user.login.lower():
            parsed = parse_qodo_comment_body(c.body or "")
            qodo_feedbacks.append(
                {"author": c.user.login, "parsed": parsed, "id": c.id}
            )
    payload = {"qodofeedback": qodo_feedbacks, "pr": args.pr, "repo": args.repo}
    input_hash = sha256_hex_of_obj({"repo": args.repo, "pr": args.pr})
    if args.dry_run:
        print("DRY RUN qodo payload:", payload)
        return
    event = emitevent(
        "qodoreader",
        payload,
        commitsha=os.environ.get("GIT_COMMIT_SHA"),
        inputhash=input_hash,
    )
    print("Wrote event:", event["provenancetoken"])


if __name__ == "__main__":
    main()
