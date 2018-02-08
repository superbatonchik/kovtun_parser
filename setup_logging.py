import os
import logging.config

import yaml

def setup_logging(path='logging.yaml', level=logging.INFO):
    with open(path, 'rt') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
