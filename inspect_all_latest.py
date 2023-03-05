from dataclasses import dataclass
from datetime import datetime, timedelta
import sys
import time
import requests
import dateparser

REPOSITORIES = [
    "quay.io/openshift-release-dev/ocp-release",
]


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


def main():
    for repo in get_repositories():
        print(repo)
        image = get_latest_image(repo)
        print(image)


if __name__ == "__main__":
    main()
