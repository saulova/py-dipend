import argparse
import re
from pathlib import Path

parser = argparse.ArgumentParser(description="Add license header.")
parser.add_argument("-p", "--package", help="Package name.")

args = parser.parse_args()

main_file_path = Path("pyproject.toml")
package_file_path = Path(f"./packages/{args.package}/pyproject.toml")


def extract_version(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if "version" in line:
                match = re.match(r'^\s*version\s*=\s*"([^"]+)"\s*$', line)
                if match:
                    return match.group(1)
    return None


def update_version(path: Path, new_version: str):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    updated_content = re.sub(r'(^\s*version\s*=\s*")[^"]+(")', lambda m: f"{m.group(1)}{new_version}{m.group(2)}", content, flags=re.MULTILINE)
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated_content)


# Extract version from main file
version = extract_version(main_file_path)

if version:
    update_version(package_file_path, version)
    print(f"Version {version} applied to {args.package} package.")
else:
    print("Could not extract version from main file.")
