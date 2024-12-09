import logging
import os
import signal
import sys

app_name = "discord-music-rpc"


def get_log_directory():
    """
    Get platform-specific application log directory.
    """
    if sys.platform == "win32":
        # Windows: Use AppData\Local\<AppName>\Logs
        log_dir = os.path.join(os.getenv("LOCALAPPDATA", ""), app_name, "Logs")
    elif sys.platform == "darwin":
        # macOS: ~/Library/Logs/<AppName>
        log_dir = os.path.join(os.path.expanduser("~/Library/Logs"), app_name)
    else:
        # Linux: ~/.local/share/<app_name>/logs or /var/log/<app_name>
        log_dir = os.path.join(os.path.expanduser("~/.local/share"), app_name, "logs")

    os.makedirs(log_dir, exist_ok=True)
    return log_dir


log_dir = get_log_directory()
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "app.log")),
        logging.StreamHandler(),  # Also log to console
    ],
)

logger = logging.getLogger(__name__)


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self):
        self.kill_now = True


killer = GracefulKiller()
