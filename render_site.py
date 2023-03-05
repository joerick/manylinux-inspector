
import json
from pathlib import Path
import jinja2

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "cache"

def combine_data():
    data = []
    for data_file in DATA_DIR.glob("*.json"):
        with data_file.open() as f:
            data.append(json.load(f))

    return data

def main():
    data = combine_data()

    jinja2_env = jinja2.Environment()
    index_template_file = BASE_DIR / 'index.html.jinja2'

    index_template = jinja2_env.from_string(index_template_file.read_text())
    index_html = index_template.render(data=data)

    site_dir = BASE_DIR / 'site'
    site_dir.mkdir(exist_ok=True)
    (site_dir / 'index.html').write_text(index_html)

if __name__ == "__main__":
    main()
    