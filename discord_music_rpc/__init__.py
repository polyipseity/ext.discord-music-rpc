import logging
import os
import signal
import sys
from pathlib import Path

from rich.logging import RichHandler

PROJECT_URL = "https://github.com/f0e/discord-music-rpc"
APP_NAME = "discord-music-rpc"

def get_config_dir():
    if sys.platform.startswith("win"):
        data_path = os.path.join(os.getenv("LOCALAPPDATA", "~/AppData/Local"), APP_NAME)
    elif sys.platform.startswith("darwin"):
        data_path = os.path.join(
            os.path.expanduser("~/Library/Application Support"), APP_NAME
        )
    else:
        data_path = os.path.join(os.path.expanduser("~/.config"), APP_NAME)

    if data_path is None:
        exit()

    os.makedirs(data_path, exist_ok=True)
    return Path(data_path).expanduser()


FORMAT = "%(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True),
    ],
)

logger = logging.getLogger(__name__)

CONFIG_DIR = get_config_dir()


class GracefulKiller:
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum=None, frame=None):
        logger.info(f"Received exit signal {signum}. Shutting down...")
        self.kill_now = True


killer = GracefulKiller()
