#!/usr/bin/env python3

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import json
import re
import subprocess
import sys
from typing import Sequence, TypedDict
from docker_container import DockerContainer


class CommandLog(TypedDict):
    command: list[str]
    return_code: int
    stderr: str
    stdout: str


def inspect_image(image: str):
    commands_log: list[CommandLog] = []

    with DockerContainer(image=image) as container:
        def call(command: Sequence[str], allow_fail=False):
            print(f'$ {command}')
            call_result = container.call(command)

            commands_log.append(
                {
                    "command": list(command),
                    "return_code": call_result.returncode,
                    "stdout": call_result.stdout,
                    "stderr": call_result.stderr,
                }
            )

            if not allow_fail and call_result.returncode != 0:
                raise subprocess.CalledProcessError(
                    call_result.returncode, command, call_result.stdout
                )

            print(f'$ {command}\n$?: {call_result.returncode}\nout: {call_result.stdout}\nerr: {call_result.stderr}\n')

            return call_result

        # os info
        call(["cat", "/etc/os-release"], allow_fail=True)
        call(["cat", "/etc/redhat-release"], allow_fail=True)

        # default environment
        call(['env'])

        # libc info
        call(["ldd", "--version"])

        # package manager
        possible_package_managers = [
            "yum", "apt-get", "apk", "dnf", "pacman", "zypper", "emerge"
        ]
        for package_manager in possible_package_managers:
            call(["which", package_manager], allow_fail=True)

        # global tools
        call(['auditwheel', '--version'], allow_fail=True)
        call(['patchelf', '--version'], allow_fail=True)
        call(['git', '--version'], allow_fail=True)
        call(['curl', '--version'], allow_fail=True)
        call(['autoconf', '--version'], allow_fail=True)
        call(['automake', '--version'], allow_fail=True)
        call(['libtool', '--version'], allow_fail=True)
        call(['sqlite3', '--version'], allow_fail=True)
        call(['openssl', 'version'], allow_fail=True)
        call(["pipx", "--version"])
        call(["pipx", "list", "--short"])

        pythons = container.call(['sh', '-c', 'echo /opt/python/*/bin/python']).stdout.strip().split(" ")

        for python_path in pythons:
            call([python_path, "--version"])
            call([python_path, "-c", "import setuptools; print(setuptools.__version__)"])
            call([python_path, "-m", "pip", "--version"])
            call([python_path, "-m", "pip", "freeze"])

    return {"log": commands_log}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Image to inspect")
    args = parser.parse_args()

    with redirect_stdout(sys.stderr):
        versions = inspect_image(args.image)

    print(json.dumps(versions, indent=2))


if __name__ == "__main__":
    main()
