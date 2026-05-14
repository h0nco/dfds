import logging
import os
from pathlib import Path
from dfds.config_loader import load_config

config = load_config()
log_file = config['log_file']
log_level = getattr(logging, config['log_level'].upper(), logging.INFO)
log_to_console = config['log_to_console']

Path(log_file).parent.mkdir(parents=True, exist_ok=True)
handlers = [logging.FileHandler(log_file, encoding='utf-8')]
if log_to_console:
    handlers.append(logging.StreamHandler())
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=handlers)
logger = logging.getLogger('dfds')