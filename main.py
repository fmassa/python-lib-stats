import ast
import glob
import os
from typing import Dict

from visitor import Visitor


def report(summary):
    print("Imports")
    print(summary["imports"])
    print("Calls")
    print(summary["calls"])
    print("Attrs")
    print(summary["attributes"])


def summarize(v: Visitor, library_name: str):
    imports = set([x for x in v.remapped.values() if x.startswith(library_name)])
    calls = set([x for x in v.called.keys() if x.startswith(library_name)])
    attrs = set([x for x in v.nets.values() if x.startswith(library_name)])
    return {"imports": imports, "calls": calls, "attributes": attrs}


def process_local_repository(local_dir: str, library_name: str) -> Dict:
    pattern = os.path.join(local_dir, "**", "*.py")
    files = glob.glob(pattern, recursive=True)

    v = Visitor()

    for fname in files:
        with open(fname, 'r') as f:
            code = f.read()
        co = ast.parse(code)
        v.visit(co)

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
