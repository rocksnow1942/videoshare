import argparse
import hashlib
import os
import re
from functools import lru_cache


@lru_cache(maxsize=None)
def get_file_hash(file):
    return hashlib.md5(open(file, "rb").read()).hexdigest()


def main(source):
    pattern = re.compile(r".*_\d\..*")
    for root, dirs, files in os.walk(source):
        for f in files:
            if pattern.match(f):
                # assume the duplicates are xxxx_1.xxx, xxxx_2.xxx etc.
                original = f.split(".")[0][:-2] + "." + f.split(".")[-1]
                original_path = os.path.join(root, original)
                duplicate_path = os.path.join(root, f)
                # check file hash
                if not os.path.exists(original_path):
                    continue
                original_hash = get_file_hash(original_path)
                duplicate_hash = get_file_hash(duplicate_path)
                if original_hash == duplicate_hash:
                    # delete duplicate
                    os.remove(duplicate_path)
                    print(f"Deleted duplicate: {duplicate_path}")
                else:
                    print(f"Wrong duplicate: {os.path.join(root, f)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", help="source folder")
    args = parser.parse_args()
    main(args.source)
