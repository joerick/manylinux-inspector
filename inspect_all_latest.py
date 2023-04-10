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


def get_latest_image(repository: Repository) -> Image | None:
    response = requests.get(
        f"https://quay.io/api/v1/repository/{repository.namespace}/{repository.name}?includeTags=true"
    )
    response.raise_for_status()
    repo_info = response.json()
    tags_dict = repo_info["tags"]

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


def inspect_image_wrapper(image: Image):
    print(f"Inspecting {image}", file=sys.stderr)
    inspect_and_save(f'quay.io/{image.repository.namespace}/{image.repository.name}:{image.tag}')
    print(f"Inspecting {image} complete.", file=sys.stderr)

executor = ThreadPoolExecutor(max_workers=4)

def main():
    images_to_inspect = []

    print("Fetching latest images...", file=sys.stderr)

    latest_images = {}

    for repo in get_repositories():
        image = get_latest_image(repo)
        if image:
            latest_images[f'quay.io/{image.repository.namespace}/{image.repository.name}'] = image.tag
            images_to_inspect.append(image)

    print(f"Found {len(images_to_inspect)} images to inspect", file=sys.stderr)
    for image in images_to_inspect:
        print(f" - {image}", file=sys.stderr)

    executor.map(inspect_image_wrapper, images_to_inspect)

    print("Writing latest images...", file=sys.stderr)
    latest_file = Path(__file__).parent / "data" / "latest.json"
    latest_file.parent.mkdir(parents=True, exist_ok=True)
    latest_file.write_text(json.dumps({
        "metadata": {
            "generated_at": time.time(),
        },
        "data": latest_images,
    }, indent=2))

    print(f"Finished.", file=sys.stderr)


if __name__ == "__main__":
    main()
