import logging
import os
import signal
import sys
from pathlib import Path

PROJECT_URL = "https://github.com/f0e/discord-music-rpc"
APP_NAME = "discord-music-rpc"


def get_log_directory():
    if sys.platform == "win32":
        log_dir = os.path.join(
            os.getenv("LOCALAPPDATA", "~/AppData/Local"), APP_NAME, "Logs"
        )
    elif sys.platform == "darwin":
        log_dir = os.path.join(os.path.expanduser("~/Library/Logs"), APP_NAME)
    else:
        log_dir = os.path.join(os.path.expanduser("~/.local/share"), APP_NAME, "logs")

    os.makedirs(log_dir, exist_ok=True)
    return Path(log_dir).expanduser()


def get_config_dir():
    if sys.platform.startswith("win"):
        data_path = os.path.join(os.getenv("LOCALAPPDATA", "~/AppData/Local"), APP_NAME)
    elif sys.platform.startswith("darwin"):
        data_path = os.path.join(
            os.path.expanduser("~/Library/Application Support"), APP_NAME
        )
    else:
        data_path = os.path.join(os.path.expanduser("~/.local/share"), APP_NAME)

    if data_path is None:
        exit()

    os.makedirs(data_path, exist_ok=True)
    return Path(data_path).expanduser()


LOG_DIR = get_log_directory()
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app.log")),
        logging.StreamHandler(),  # Also log to console
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
