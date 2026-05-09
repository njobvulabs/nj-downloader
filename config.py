import json
import os

CONFIG_DIR = os.path.expanduser('~/.config/nj-downloader')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

DEFAULT = {
    'theme': 'Dark',
    'output_dir': os.path.expanduser('~/Downloads/nj-downloader'),
}


def load():
    try:
        with open(CONFIG_PATH) as f:
            return {**DEFAULT, **json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT)


def save(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
