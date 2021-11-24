import ast
from collections import defaultdict
import glob
import os
from typing import Dict

from visitor import Visitor


def _my_print(data, l):
    k = " "
    v = "| Count"
    title = "{:>" + str(l) + "s}"
    print(title.format(v))
    print("-" * l)
    for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True):
        print(f"    {k:<64}: {v}")


def report(summary):
    l = 75
    sep = "=" * l
    title = "{:^" + str(l) + "s}"
    print(sep)
    print(title.format("Imports"))
    print(sep)
    _my_print(summary["import_count"], l)
    print(sep)
    print(title.format("Calls"))
    print(sep)
    _my_print(summary["call_count"], l)
    print(sep)
    print(title.format("Attrs"))
    print(sep)
    _my_print(summary["access_count"], l)


def summarize(v: Visitor, library_name: str):
    def filter_fn(item):
        k, v = item
        return k.startswith(library_name)
    res = {}
    for field in ["import_count", "call_count", "access_count"]:
        generator = filter(filter_fn, getattr(v, field).items())
        res[field] = {k: val for k, val in generator}
    return res


def aggregate(summaries):
    res = {}
    res["import_count"] = defaultdict(int)
    res["call_count"] = defaultdict(int)
    res["access_count"] = defaultdict(int)
    count_used = 0
    for summary in summaries:
        has_appeared = False
        for field, subsummary in summary.items():
            for k, v in subsummary.items():
                res[field][k] += 1# v
                has_appeared = True
        count_used += int(has_appeared)
    return res, count_used


def process_local_repository(local_dir: str, library_name: str) -> Dict:
    pattern = os.path.join(local_dir, "**", "*.py")
    files = glob.glob(pattern, recursive=True)

    v = Visitor()

    skipped_files = 0
    for fname in files:
        with open(fname, 'r') as f:
            code = f.read()
        try:
            co = ast.parse(code)
        except SyntaxError:
            skipped_files += 1
            # print(f"Skipping {fname} due to SyntaxError")
            continue
        v.visit(co)

    if skipped_files > 0:
        print(f"Skipped {skipped_files} out of {len(files)} files due to SyntaxError in {local_dir}")
    summary = summarize(v, library_name)
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find imports and function calls in Python repos")
    parser.add_argument("--local_dir", type=str, help="repo path")
    parser.add_argument("--library_name", type=str, help="name of the library of interest")
    parser.add_argument("--absolute_count", dest="absolute_count", action="store_true",
        help="Whether to consider the absolute counts of the elements retrieved, "
             "or only the presence or not in each immediate folder from local_dir")
    parser.set_defaults(absolute_count=False)

    args = parser.parse_args()
    if args.absolute_count:
        summary = process_local_repository(args.local_dir, args.library_name)
    else:
        directories = [x for x in os.listdir(args.local_dir) if os.path.isdir(os.path.join(args.local_dir, x))]
        s = []
        for d in directories:
            s.append(process_local_repository(os.path.join(args.local_dir, d), args.library_name))
        summary, count_used = aggregate(s)
        print(f"Total number of projects that use {args.library_name}: {count_used} / {len(directories)}")

    report(summary)
