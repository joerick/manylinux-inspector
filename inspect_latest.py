import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import time
import requests
import dateparser
from inspect_and_save import inspect_and_save


@dataclass
class Repository:
    namespace: str
    name: str


def get_repositories() -> list[Repository]:
    response = requests.get(
        "https://quay.io/api/v1/repository?public=true&namespace=pypa"
    )
    response.raise_for_status()
    repository_dicts = response.json()["repositories"]

    return [
        Repository(
            namespace=d["namespace"],
            name=d["name"],
        )
        for d in repository_dicts
    ]


@dataclass
class Image:
    repository: Repository
    tag: str


def fetch_repo_tags(repository: Repository) -> dict:
    response = requests.get(
        f"https://quay.io/api/v1/repository/{repository.namespace}/{repository.name}?includeTags=true"
    )
    response.raise_for_status()
    repo_info = response.json()
    return repo_info["tags"]


def get_latest_image(repository: Repository) -> Image | None:
    tags_dict = fetch_repo_tags(repository)

    latest_tag = tags_dict.pop("latest")
    if not latest_tag:
        print(f'No "latest" tag found for {repository}', file=sys.stderr)
        return None

    updated_timestamp = dateparser.parse(latest_tag["last_modified"])
    if not updated_timestamp:
        print(f'Unable to parse timestamp {latest_tag["last_modified"]}', file=sys.stderr)
        return None

    time_since_update = time.time() - updated_timestamp.timestamp()
    ONE_YEAR = 365 * 24 * 60 * 60

    if time_since_update > ONE_YEAR:
        print(f'Image {repository}:latest is {time_since_update / 24 / 60 / 60:.0f} days old, ignoring', file=sys.stderr)
        return None

    # find the tag whose manifest matches 'latest'
    tag_name = next(
        name
        for (name, info) in tags_dict.items()
        if info["manifest_digest"] == latest_tag["manifest_digest"]
    )

    return Image(repository=repository, tag=tag_name)


def get_images(repository: Repository, *, within_days: int) -> list[Image]:
    tags_dict = fetch_repo_tags(repository)

    images = []

    for tag_name, tag_info in tags_dict.items():
        if tag_name == "latest":
            # already handled elsewhere
            continue

        updated_timestamp = dateparser.parse(tag_info["last_modified"])
        if not updated_timestamp:
            print(f'Unable to parse timestamp {tag_info["last_modified"]}', file=sys.stderr)
            continue

        within_seconds = within_days * 24 * 60 * 60
        earliest_timestamp = time.time() - within_seconds
        if updated_timestamp.timestamp() > earliest_timestamp:
            images.append(Image(repository=repository, tag=tag_name))

    return images


def inspect_image_wrapper(image: Image):
    print(f"Inspecting {image}", file=sys.stderr)
    inspect_and_save(f'quay.io/{image.repository.namespace}/{image.repository.name}:{image.tag}')
    print(f"Inspecting {image} complete.", file=sys.stderr)

executor = ThreadPoolExecutor(max_workers=4)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--within-days",
        type=int,
        help="Inspect images updated in the last N days. If not specified, only the latest image is inspected.",
    )

    args = parser.parse_args()

    images_to_inspect: list[Image] = []

    print("Fetching latest images...", file=sys.stderr)

    latest_images = {}

    for repo in get_repositories():
        image = get_latest_image(repo)
        if image:
            latest_images[f'quay.io/{image.repository.namespace}/{image.repository.name}'] = image.tag
            images_to_inspect.append(image)

        if args.within_days is not None:
            previous_images = get_images(repo, within_days=args.within_days)
            for image in previous_images:
                if image not in images_to_inspect:
                    images_to_inspect.append(image)

    print(f"Found {len(images_to_inspect)} images to inspect", file=sys.stderr)
    for image in images_to_inspect:
        print(f" - {image}", file=sys.stderr)

    print("Inspecting images...", file=sys.stderr)
    inspect_results = executor.map(inspect_image_wrapper, images_to_inspect)

    # access the results to make sure they're all done
    print("Inspection results:", list(inspect_results), file=sys.stderr)

    latest_file = Path(__file__).parent / "data" / "latest.json"
    prev_latest_images = {}

    if latest_file.exists():
        prev_latest_images = json.loads(latest_file.read_text())["data"]

    if prev_latest_images == latest_images:
        print("No changes to latest images, not writing.", file=sys.stderr)
    else:
        print("Writing latest images...", file=sys.stderr)
        latest_file.parent.mkdir(parents=True, exist_ok=True)
        latest_file.write_text(json.dumps({
            "metadata": {
                "last_updated": time.time(),
            },
            "data": latest_images,
        }, indent=2))

    print(f"Finished.", file=sys.stderr)


if __name__ == "__main__":
    main()
