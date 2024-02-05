import os
import shutil
import argparse

prefixes = [
    "hhd800.com@",
    "zzpp08.com@",
]


def main(target_dir, dry_run=False):
    for root, dirs, files in os.walk(target_dir):
        for filename in files:
            for prefix in prefixes:
                if filename.startswith(prefix):
                    new_filename = filename[len(prefix) :]
                    print(f"Renaming {filename} to {new_filename}")
                    if not dry_run:
                        shutil.move(
                            os.path.join(root, filename),
                            os.path.join(root, new_filename),
                        )
                    break


parser = argparse.ArgumentParser()
parser.add_argument(
    "target_dir", help="Directory containing files to process", default="."
)
parser.add_argument(
    "--execute",
    help="Executes, mutating data on disk, if not proided, dryruns",
    action="store_true",
)
args = parser.parse_args()

main(args.target_dir, dry_run=not args.execute)
