import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from inspect_image import inspect_image

PROJECT_DIR = Path(__file__).parent
REPORTS_DIR = PROJECT_DIR / "data" / "reports"


def inspect_and_save(image: str, *, force: bool = False):
    report_filename = image.replace("/", "_").replace(":", "_") + ".json"
    report_file = REPORTS_DIR / report_filename

    if report_file.exists() and not force:
        print("Already inspected, use `force` argument to re-inspect", file=sys.stderr)
        return

    inspect_data = inspect_image(image)

    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps({
        "metadata": {
            "image": image,
            "generated_at": time.time(),
        },
        "data": inspect_data,
    }, indent=2))

    print(f"Done. Saved to {report_file}", file=sys.stderr)


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
