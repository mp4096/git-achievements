#!/usr/bin/env python3

import argparse
import statistics
import os
import sys
import subprocess
from typing import Optional, Iterator, Tuple


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


def get_commit_message(repo_path: str, revision: str) -> str:
    result = subprocess.run(
        ["git", "show", "--no-patch", "--format=%B", revision],
        cwd=os.path.abspath(repo_path),
        stdout=subprocess.PIPE,
    )
    return result.stdout.decode("utf-8").strip()


def get_length_stats(
    repo_path: str,
    author: Optional[str] = None,
    after: Optional[str] = None,
    rev_list_args: Optional[str] = None,
) -> Tuple[int, int, int, float, float]:
    messages = [
        get_commit_message(repo_path, r)
        for r in get_commits_list(repo_path, author, after, rev_list_args)
    ]
    lengths = [len(m) for m in messages]
    return (
        len(lengths),
        min(lengths),
        max(lengths),
        statistics.median(lengths),
        statistics.mean(lengths),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get git commit message stats.")
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
    parser.add_argument("repo_path", type=str, help="path to the repo")
    args = parser.parse_args(sys.argv[1:])

    total_num, min_length, max_length, median, mean = get_length_stats(
        args.repo_path, args.author, args.after, args.rev_list_args
    )
    print("Commit message stats:")
    print("  total number of commits: {:4d}".format(total_num))
    print("               min length: {:4d}".format(min_length))
    print("            median length: {:7.2f}".format(median))
    print("              mean length: {:7.2f}".format(mean))
    print("               max length: {:4d}".format(max_length))
