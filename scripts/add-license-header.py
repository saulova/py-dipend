import os
import argparse
import zipfile
import tarfile
import tempfile
from pathlib import Path

parser = argparse.ArgumentParser(description="Add license header.")
parser.add_argument("-p", "--package", help="Package name.")

args = parser.parse_args()

LICENSE_HEADER = {}

LICENSE_HEADER[".py"] = """\
# Copyright 2025 Saulo V. Alvarenga. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

LICENSE_HEADER[".js"] = """\
/*
 * Copyright 2025 Saulo V. Alvarenga. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

"""


def apply_license_header(file: Path):
    license_header = LICENSE_HEADER.get(file.suffix, None)

    if license_header is None:
        return

    content = file.read_text(encoding="utf-8")

    if license_header.strip() not in content:
        file.write_text(license_header + content, encoding="utf-8")


def patch_whl(whl_path: Path):
    with tempfile.TemporaryDirectory("whl") as tmpdir:
        tmp = Path(tmpdir)
        with zipfile.ZipFile(whl_path, "r") as zin:
            zin.extractall(tmp)

        for file in tmp.rglob("*"):
            apply_license_header(file)

        with zipfile.ZipFile(whl_path, "w") as zout:
            for file in tmp.rglob("*"):
                zout.write(file, file.relative_to(tmp))


def patch_tar_gz(tar_path: Path):
    with tempfile.TemporaryDirectory("tar_gz") as tmpdir:
        tmp = Path(tmpdir)
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(tmp, filter="fully_trusted")

        for file in tmp.rglob("*"):
            apply_license_header(file)

        temp_tar_path = tar_path.with_suffix(tar_path.suffix + ".temp")
        with tarfile.open(temp_tar_path, "w:gz") as temp_tar:
            for file in tmp.rglob("*"):
                if file.is_file():
                    temp_tar.add(file, arcname=file.relative_to(tmp))

        os.replace(temp_tar_path, tar_path)


def main():
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("Missing 'dist/' folder.")
        return
    for file in dist_dir.iterdir():
        if file.name.startswith(f"{args.package.replace('-', '_')}-"):
            if file.suffix == ".whl":
                print(f"Patching wheel: {file.name}")
                patch_whl(file)
            elif file.suffix == ".gz":
                print(f"Patching sdist: {file.name}")
                patch_tar_gz(file)

    print("License header addition complete.")


if __name__ == "__main__":
    main()
