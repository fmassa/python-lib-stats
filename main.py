import ast
import glob
import os
from typing import Dict

from visitor import Visitor


def _my_print(data):
    for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True):
        print(f"    {k:<65}: {v}")


def report(summary):
    sep = "=" * 75
    print(sep)
    print("Imports")
    print(sep)
    _my_print(summary["imports"])
    print(sep)
    print("Calls")
    print(sep)
    _my_print(summary["calls"])
    print(sep)
    print("Attrs")
    print(sep)
    _my_print(summary["attributes"])


def summarize(v: Visitor, library_name: str):
    imports = {k: val for k, val in v.import_count.items() if k.startswith(library_name)}
    calls = {k: val for k, val in v.call_count.items() if k.startswith(library_name)}
    attrs = {k: val for k, val in v.access_count.items() if k.startswith(library_name)}
    return {"imports": imports, "calls": calls, "attributes": attrs}


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

    print(f"Skipped {skipped_files} out of {len(files)} files due to SyntaxError")
    summary = summarize(v, library_name)
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find imports and function calls in Python repos")
    parser.add_argument("--local_dir", type=str, help="repo path")
    parser.add_argument("--library_name", type=str, help="name of the library of interest")

    args = parser.parse_args()
    summary = process_local_repository(args.local_dir, args.library_name)
    report(summary)
