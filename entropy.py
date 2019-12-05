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
    repo_path: str, author: Optional[str] = None, after: Optional[str] = None
) -> Iterator[str]:
    args = []
    if author:
        args.append("--author={:s}".format(author))
    if after:
        args.append("--after={:s}".format(after))
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
    repo_path: str, author: Optional[str] = None, after: Optional[str] = None
) -> float:
    tally_counter_files: Counter = Counter()
    for r in get_commits_list(repo_path, author, after):
        tally_counter_files.update(get_changed_files(repo_path, r))
    total = len(tally_counter_files)
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
    parser.add_argument("repo_path", type=str, help="path to the repo")
    args = parser.parse_args(sys.argv[1:])

    print(get_entropy(args.repo_path, args.author, args.after))
