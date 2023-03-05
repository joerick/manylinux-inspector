import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

PROJECT_DIR = Path(__file__).parent
CACHE_DIR = PROJECT_DIR / "cache"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Image to inspect")
    parser.add_argument(
        "-f", "--force", action="store_true", help="Force re-inspection"
    )
    args = parser.parse_args()

    cache_filename = args.image.replace("/", "_").replace(":", "_") + ".json"
    cache_file = CACHE_DIR / cache_filename

    if cache_file.exists() and not args.force:
        print("Already inspected, use --force to re-inspect", file=sys.stderr)
        return

    process = subprocess.run([sys.executable, "inspect_image.py", args.image], check=True, stdout=subprocess.PIPE)
    inspect_data = json.loads(process.stdout)

    cache_file.write_bytes(json.dumps({
        "metadata": {
            "image": args.image,
            "generated_at": time.time(),
        },
        "data": inspect_data,
    }))

    print(f"Done. Saved to {cache_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
