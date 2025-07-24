import json
import logging
import os


def load_meta_posts():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config/meta'))
    logging.info(f'Loading meta posts from {base_dir}')
    config_path = os.path.join(base_dir, 'posts.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)['posts']
