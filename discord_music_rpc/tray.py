import os
import subprocess
import sys

from PIL import Image
from pystray import Icon, Menu, MenuItem

from . import LOG_DIR, killer
from .sources import TrackWithSource


def on_quit(icon, item):
    killer.exit_gracefully()
    icon.stop()


def open_logs(icon, item):
    log_file = os.path.join(LOG_DIR, "app.log")

    if os.path.exists(log_file):
        if sys.platform.startswith("darwin"):  # macOS
            subprocess.call(("open", log_file))
        elif sys.platform.startswith("win"):  # Windows
            os.startfile(log_file)
        elif sys.platform.startswith("linux"):  # Linux
            subprocess.call(("xdg-open", log_file))


def update_tray(icon, track: TrackWithSource | None):
    menu_items = [
        MenuItem("Discord Music RPC", lambda icon, item: None, enabled=False),
        MenuItem("View Logs", open_logs),
        MenuItem("Quit", on_quit),
    ]

    if track:
        menu_items.insert(
            1,
            MenuItem(
                f"{track.track.artist} - {track.track.name}",
                lambda icon, item: None,
                enabled=False,
            ),
        )

    icon.menu = Menu(*menu_items)


def run_tray_icon() -> Icon:
    icon_path = os.path.join(os.path.dirname(__file__), "resources/cd.png")

    icon_image = Image.open(icon_path)

    menu = Menu(
        MenuItem("Discord Music RPC", lambda icon, item: None, enabled=False),
        MenuItem("View Logs", open_logs),
        MenuItem("Quit", on_quit),
    )

    icon = Icon("discord-music-rpc", icon_image, menu=menu)

    icon.run_detached()  # todo: fix on mac

    return icon
