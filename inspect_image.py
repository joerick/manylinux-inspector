#!/usr/bin/env python3

import argparse
import json
from pathlib import PurePosixPath
import re
import subprocess
from oci_container import OCIContainer

ContainerPath = PurePosixPath


def re_extract(regex: str, input: str):
    match = re.search(regex, input)
    if not match:
        return None
    return match.group(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Image to inspect")
    args = parser.parse_args()

    versions = {}
    with OCIContainer(image=args.image) as container:
        pipx_list_output = container.call(["pipx", "list", "--short"], capture_output=True).strip().splitlines()
        for line in pipx_list_output:
            name, _, version = line.partition(' ')
            versions[name] = version

        pythons = container.glob(ContainerPath("/opt/python/"), "*/bin/python")

        versions["pipx"] = container.call(["pipx", "--version"], capture_output=True).strip()
        
        versions["pythons"] = {}
        for python_path in pythons:
            python_identifier = re_extract(
                r"/opt/python/(.*)/bin/python", str(python_path)
            )
            assert python_identifier
            versions["pythons"][python_identifier] = inspect_python(
                container, python_path, python_identifier
            )

    print(json.dumps(versions, indent=2))


def inspect_python(
    container: OCIContainer, python_path: ContainerPath, python_identifier: str
):
    versions: dict[str, str] = {}
    is_pypy = "pypy" in python_identifier
    if not is_pypy:
        versions["python"] = re_extract(
            r"Python (\S+)",
            container.call([python_path, "--version"], capture_output=True),
        )
    else:
        versions["python"] = re_extract(
            r"PyPy (\S+)",
            container.call([python_path, "--version"], capture_output=True),
        )

    versions["setuptools"] = container.call(
        [python_path, "-c", "import setuptools; print(setuptools.__version__)"],
        capture_output=True,
    ).strip()

    pip_version_output = container.call(
        [python_path, "-m", "pip", "--version"], capture_output=True
    )
    versions["pip"] = re_extract(r"pip (\S+)", pip_version_output)

    pip_freeze_output = container.call(
        [python_path, "-m", "pip", "freeze"], capture_output=True
    ).strip().splitlines()

    for line in pip_freeze_output:
        name, _, version = line.partition('==')
        versions[name] = version

    return versions


if __name__ == "__main__":
    main()
