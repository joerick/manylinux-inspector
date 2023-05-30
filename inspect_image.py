#!/usr/bin/env python3

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import subprocess
import sys
import uuid
from contextlib import redirect_stdout
from types import TracebackType
from typing import Sequence, TypedDict


class CommandLog(TypedDict):
    command: list[str]
    return_code: int
    stderr: str
    stdout: str


def inspect_image(image: str):
    commands_log: list[CommandLog] = []

    with DockerContainer(image=image) as container:
        def call(command: Sequence[str], allow_fail=False):
            print(f"$ {command}")
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

            print(
                f"$ {command}\n$?: {call_result.returncode}\nout: {call_result.stdout}\nerr: {call_result.stderr}\n"
            )

            return call_result

        def glob(pattern: str) -> list[str]:
            call_result = call(["sh", "-c", f"ls -d {pattern}"], allow_fail=True)
            if call_result.returncode != 0:
                return []
            return call_result.stdout.strip().split("\n")

        # os info
        call(["cat", "/etc/os-release"], allow_fail=True)
        call(["cat", "/etc/redhat-release"], allow_fail=True)

        # default environment
        call(["env"])

        # libc info
        call(["ldd", "--version"], allow_fail=True)
        for musl_libc in glob("/lib/libc.musl-*"):
            # musl libc can be opened as a program, it prints its version
            call([musl_libc], allow_fail=True)

        # package manager
        possible_package_managers = [
            "yum",
            "apt-get",
            "apk",
            "dnf",
            "pacman",
            "zypper",
            "emerge",
        ]
        for package_manager in possible_package_managers:
            call(["which", package_manager], allow_fail=True)

        # global tools
        call(["auditwheel", "--version"], allow_fail=True)
        call(["patchelf", "--version"], allow_fail=True)
        call(["git", "--version"], allow_fail=True)
        call(["curl", "--version"], allow_fail=True)
        call(["autoconf", "--version"], allow_fail=True)
        call(["automake", "--version"], allow_fail=True)
        call(["libtool", "--version"], allow_fail=True)
        call(["sqlite3", "--version"], allow_fail=True)
        call(["openssl", "version"], allow_fail=True)
        call(["pipx", "--version"])
        call(["pipx", "list", "--short"])

        pythons = glob('/opt/python/*/bin/python')

        for python_path in pythons:
            call([python_path, "--version"])
            call([python_path, "-m", "pip", "list", "--format=freeze"])

    return {"log": commands_log}


class DockerContainer:
    UTILITY_PYTHON = "/opt/python/cp38-cp38/bin/python"

    def __init__(
        self,
        *,
        image: str,
        simulate_32_bit: bool = False,
    ):
        if not image:
            msg = "Must have a non-empty image to run."
            raise ValueError(msg)

        self.image = image
        self.simulate_32_bit = simulate_32_bit
        self.name: str | None = None

    def __enter__(self) -> DockerContainer:
        self.name = f"manylinuxinspector-{uuid.uuid4()}"

        subprocess.run(
            [
                "docker",
                "run",
                f"--name={self.name}",
                "--detach",
                "--tty",
                self.image,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )

        noop_result = self.call(["/bin/true"])
        assert noop_result.returncode == 0, noop_result.stderr

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        assert isinstance(self.name, str)

        # remove the container
        subprocess.run(
            ["docker", "rm", "--force", "-v", self.name],
            stdout=subprocess.DEVNULL,
            check=False,
        )
        if "CLEANUP_OLD_IMAGES" in os.environ:
            subprocess.run(
                ["docker", "rmi", "--force", self.image],
                check=False,
            )
            subprocess.run(
                ["docker", "image", "prune", "--force"],
                check=False,
            )

        self.name = None

    def call(self, args: Sequence[str]) -> CallResult:
        assert isinstance(self.name, str)

        if self.simulate_32_bit:
            args = ["linux32", *args]

        run_result = subprocess.run(
            ["docker", "exec", self.name, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            encoding="utf-8",
            errors="surrogateescape",
        )

        return DockerContainer.CallResult(
            returncode=run_result.returncode,
            stdout=run_result.stdout,
            stderr=run_result.stderr,
        )

    @dataclasses.dataclass
    class CallResult:
        returncode: int
        stdout: str
        stderr: str

        def __bool__(self) -> bool:
            return self.returncode == 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Image to inspect")
    args = parser.parse_args()

    with redirect_stdout(sys.stderr):
        versions = inspect_image(args.image)

    print(json.dumps(versions, indent=2))


if __name__ == "__main__":
    main()
