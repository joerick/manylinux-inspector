from __future__ import annotations
import dataclasses

import subprocess
import uuid
from types import TracebackType
from typing import Sequence


@dataclasses.dataclass
class CallResult:
    returncode: int
    stdout: str
    stderr: str

    def __bool__(self) -> bool:
        return self.returncode == 0


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

        subprocess.run(
            ["docker", "rm", "--force", "-v", self.name],
            stdout=subprocess.DEVNULL,
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

        return CallResult(
            returncode=run_result.returncode,
            stdout=run_result.stdout,
            stderr=run_result.stderr,
        )
