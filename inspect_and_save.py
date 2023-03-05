import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from inspect_image import inspect_image

PROJECT_DIR = Path(__file__).parent
CACHE_DIR = PROJECT_DIR / "cache"


def inspect_and_save(image: str, *, force: bool = False):
    cache_filename = image.replace("/", "_").replace(":", "_") + ".json"
    cache_file = CACHE_DIR / cache_filename

    if cache_file.exists() and not force:
        print("Already inspected, use `force` argument to re-inspect", file=sys.stderr)
        return

    inspect_data = inspect_image(image)

    cache_file.write_text(json.dumps({
        "metadata": {
            "image": image,
            "generated_at": time.time(),
        },
        "data": inspect_data,
    }))

    print(f"Done. Saved to {cache_file}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Image to inspect")
    parser.add_argument(
        "-f", "--force", action="store_true", help="Force re-inspection"
    )
    args = parser.parse_args()

    return inspect_and_save(args.image, force=args.force)

if __name__ == "__main__":
    main()
