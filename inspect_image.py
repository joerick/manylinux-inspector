#!/usr/bin/env python3

import argparse
import json
from pathlib import PurePosixPath
import re
import subprocess
from oci_container import OCIContainer

ContainerPath = PurePosixPath

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Image to inspect")
    args = parser.parse_args()

    versions = {}
    with OCIContainer(image=args.image) as container:
        auditwheel_output = container.call(["auditwheel", "--version"], capture_output=True)
        versions["auditwheel"] = re.search(r"auditwheel (\d+\.\d+\.\d+)", auditwheel_output).group(1)

        pythons = container.glob(ContainerPath("/opt/python/"), "*/bin/python")
        print (pythons)
        for python_path in pythons:
            inspect_python(container, python_path)

    
    print(json.dumps(versions))

def inspect_python(container: OCIContainer, python_path: ContainerPath):
    container.call([python_path, "-c", "import auditwheel; print(auditwheel)"], capture_output=True)

if __name__ == "__main__":
    main()