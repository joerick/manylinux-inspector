#!/usr/bin/env python3

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import json
from pathlib import PurePosixPath
import re
import shlex
import subprocess
import sys
from typing import Callable, Sequence, TypedDict
from oci_container import OCIContainer, PathOrStr

ContainerPath = PurePosixPath


class CommandLog(TypedDict):
    command: list[str]
    return_code: int
    output: str


def re_extract(regex: str, input: str):
    match = re.search(regex, input)
    if not match:
        return None
    return match.group(1)


def inspect_image(image: str):
    report = {}
    commands_log: list[CommandLog] = []

    with OCIContainer(image=image) as container:
        def call(command: Sequence[PathOrStr], allow_fail=False, capture_stderr=True):
            if capture_stderr:
                actual_command = ["sh", "-c", f"{shlex.join(str(a) for a in command)} 2>&1"]
            else:
                actual_command = command

            try:
                output = container.call(actual_command, capture_output=True)
                return_code = 0
            except subprocess.CalledProcessError as e:
                if not allow_fail:
                    raise
                output = e.output
                return_code = e.returncode

            commands_log.append(
                {
                    "command": list(str(arg) for arg in command),
                    "return_code": return_code,
                    "output": output,
                }
            )

            return output

        # os info
        call(["cat", "/etc/os-release"], allow_fail=True)
        call(["cat", "/etc/redhat-release"], allow_fail=True)

        # libc info
        call(["ldd", "--version"])

        pipx_list_output = call(["pipx", "list", "--short"]).strip().splitlines()
        for line in pipx_list_output:
            name, _, version = line.partition(" ")
            report[name] = version

        pythons = container.glob(ContainerPath("/opt/python/"), "*/bin/python")

        report["pipx"] = call(
            ["pipx", "--version"],
        ).strip()

        report["pythons"] = {}
        for python_path in pythons:
            python_identifier = re_extract(
                r"/opt/python/(.*)/bin/python", str(python_path)
            )
            assert python_identifier
            report["pythons"][python_identifier] = inspect_python(
                call, python_path, python_identifier
            )

    report["log"] = commands_log

    return report


def inspect_python(
    call: Callable[[Sequence[PathOrStr]], str],
    python_path: ContainerPath,
    python_identifier: str,
):
    versions: dict[str, str | None] = {}
    is_pypy = "pypy" in python_identifier
    if not is_pypy:
        versions["python"] = re_extract(
            r"Python (\S+)",
            call([python_path, "--version"]),
        )
    else:
        versions["python"] = re_extract(
            r"PyPy (\S+)",
            call([python_path, "--version"]),
        )

    versions["setuptools"] = call(
        [python_path, "-c", "import setuptools; print(setuptools.__version__)"],
    ).strip()

    pip_version_output = call([python_path, "-m", "pip", "--version"])
    versions["pip"] = re_extract(r"pip (\S+)", pip_version_output)

    pip_freeze_output = call([python_path, "-m", "pip", "freeze"]).strip().splitlines()

    for line in pip_freeze_output:
        name, _, version = line.partition("==")
        versions[name] = version

    return versions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Image to inspect")
    args = parser.parse_args()

    with redirect_stdout(sys.stderr):
        versions = inspect_image(args.image)

    print(json.dumps(versions, indent=2))


if __name__ == "__main__":
    main()
