#!/usr/bin/env python3

import argparse
from collections import Counter
import math
import os
import sys
import subprocess
from typing import Optional, Iterable, Iterator


def compute_entropy(normalized_probabilities: Iterable[float]) -> float:
    return -sum(p * math.log2(p) for p in normalized_probabilities)


def get_commits_list(
    repo_path: str,
    author: Optional[str] = None,
    after: Optional[str] = None,
    rev_list_args: Optional[str] = None,
) -> Iterator[str]:
    args = []
    if author:
        args.append("--author={:s}".format(author))
    if after:
        args.append("--after={:s}".format(after))
    if rev_list_args:
        args.extend(rev_list_args.split())
    result = subprocess.run(
        ["git", "rev-list"] + args + ["HEAD"],
        cwd=os.path.abspath(repo_path),
        stdout=subprocess.PIPE,
    )
    return filter(None, result.stdout.decode("utf-8").split("\n"))


def get_changed_files(repo_path: str, revision: str) -> Iterator[str]:
    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", revision],
        cwd=os.path.abspath(repo_path),
        stdout=subprocess.PIPE,
    )
    return filter(None, result.stdout.decode("utf-8").split("\n"))


def get_entropy(
    repo_paths: Iterable[str],
    author: Optional[str] = None,
    after: Optional[str] = None,
    rev_list_args: Optional[str] = None,
) -> float:
    tally_counter_files = Counter(
        os.path.join(os.path.abspath(repo), f)
        for repo in repo_paths
        for revision in get_commits_list(repo, author, after, rev_list_args)
        for f in get_changed_files(repo, revision)
    )
    total = sum(tally_counter_files.values())
    if total == 0:
        raise RuntimeError("No changed files for the query")
    return compute_entropy(v / total for v in tally_counter_files.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute entropy of git commits based on touched files."
    )
    parser.add_argument(
        "--author", type=str, default="", required=False, help="author email"
    )
    parser.add_argument(
        "--after", type=str, default="", required=False, help="after timestamp"
    )
    parser.add_argument(
        "--rev-list-args",
        type=str,
        default="",
        required=False,
        help="any further arguments for git rev-list",
    )
    parser.add_argument("repo_paths", type=str, nargs="+", help="path to the repos")
    args = parser.parse_args(sys.argv[1:])

    print(get_entropy(args.repo_paths, args.author, args.after, args.rev_list_args))
