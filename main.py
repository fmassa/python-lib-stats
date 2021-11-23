import glob
import os
import ast
from visitor import Visitor


def report(v: Visitor, library_name: str):
    print("Imports")
    print(set([x for x in v.remapped.values() if x.startswith(library_name)]))
    print("Calls")
    print(set([x for x in v.called.keys() if x.startswith(library_name)]))
    print("Attrs")
    print(set([x for x in v.nets.values() if x.startswith(library_name)]))


def process_local_repository(local_dir: str, library_name: str):
    pattern = os.path.join(local_dir, "**", "*.py")
    files = glob.glob(pattern, recursive=True)

    v = Visitor()

    for fname in files:
        with open(fname, 'r') as f:
            code = f.read()
        co = ast.parse(code)
        v.visit(co)

    report(v, library_name)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find imports and function calls in Python repos")
    parser.add_argument("--local_dir", type=str, help="repo path")
    parser.add_argument("--library_name", type=str, help="name of the library of interest")

    args = parser.parse_args()
    process_local_repository(args.local_dir, args.library_name)
