from dataclasses import dataclass
import gzip
import json
from pathlib import Path
import re
import shutil

WEBAPP_DIR = Path(__file__).parent
BASE_DIR = WEBAPP_DIR.parent
INPUT_DATA_DIR = BASE_DIR / "data"
INPUT_LATEST_FILE = INPUT_DATA_DIR / "latest.json"
INPUT_REPORTS_DIR = INPUT_DATA_DIR / "reports"

OUTPUT_DATA_DIR = WEBAPP_DIR / "src" / "data"


@dataclass
class ImageNameParts:
    domain: str
    org: str
    name: str
    arch: str
    tag: str

    @staticmethod
    def from_image_name(image_name: str):
        regex = r'^(?P<domain>.*)/(?P<org>.*)/(?P<name>[a-z]*(?:\d|\d\d\d\d|(?:_\d+)+))_(?P<arch>.*):(?P<tag>.*)$'
        match = re.match(regex, image_name)
        if not match:
            raise ValueError(f"Image name {image_name} does not match regex {regex}")
        return ImageNameParts(**match.groupdict())


def generate_versions_reports():
    reports_files = list(INPUT_REPORTS_DIR.glob("*.json"))
    reports = [json.loads(f.read_text()) for f in reports_files]

    reports_by_versions: dict[tuple, dict[str, dict]] = {}
    for report in reports:
        image_name = report["metadata"]["image"]
        report_name_parts = ImageNameParts.from_image_name(image_name)

        # we want to group the archs together, because they're normally the same
        version_id = (report_name_parts.domain, report_name_parts.org, report_name_parts.name, report_name_parts.tag)
        if version_id not in reports_by_versions:
            reports_by_versions[version_id] = {}

        reports_by_versions[version_id][report_name_parts.arch] = report

    result = []

    for version_id, reports in reports_by_versions.items():
        domain, org, name, tag = version_id
        combined_report = {
            "metadata": {
                "domain": domain,
                "org": org,
                "name": name,
                "tag": tag,
            },
            "reports_by_arch": reports
        }

        combined_report_file = OUTPUT_DATA_DIR / "versions" / f"{domain}_{org}_{name}_{tag}.json"
        combined_report_file.parent.mkdir(parents=True, exist_ok=True)
        combined_report_file.write_text(json.dumps(combined_report, indent=2))

        result.append({
            "domain": domain,
            "org": org,
            "name": name,
            "tag": tag,
            "filename": combined_report_file.name,
        })

    return result


def main():
    versions_reports_index = generate_versions_reports()

    index_data = {
        "versions_reports": versions_reports_index,
        "latest": json.loads(INPUT_LATEST_FILE.read_text()),
    }
    json_data = json.dumps(index_data, indent=2)

    index_file = OUTPUT_DATA_DIR / "index.json"
    index_file.write_text(json_data)

    compressed_file = index_file.with_suffix(".json.gz")
    with gzip.open(compressed_file, 'w') as f:
        f.write(json_data.encode('utf-8'))


if __name__ == "__main__":
    main()
