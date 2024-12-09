import os
import subprocess
import sys
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image
from . import killer, log_dir


def on_quit(icon, item):
    killer.exit_gracefully()
    icon.stop()


def open_logs(icon, item):
    log_file = os.path.join(log_dir, "app.log")

    if os.path.exists(log_file):
        if sys.platform.startswith("darwin"):  # macOS
            subprocess.call(("open", log_file))
        elif sys.platform.startswith("win"):  # Windows
            os.startfile(log_file)
        elif sys.platform.startswith("linux"):  # Linux
            subprocess.call(("xdg-open", log_file))


def update_tray(icon, track):
    icon.menu = Menu(
        MenuItem("Discord Music RPC", lambda icon, item: None, enabled=False),
        MenuItem(
            f"{track.artist} - {track.name}",
            lambda icon, item: None,
            enabled=False,
        ),
        MenuItem("View Logs", open_logs),
        MenuItem("Quit", on_quit),
    )


def run_tray_icon():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "../assets/cd.png")

    icon_image = Image.open(icon_path)

    menu = Menu(
        MenuItem("Discord Music RPC", lambda icon, item: None, enabled=False),
        MenuItem("View Logs", open_logs),
        MenuItem("Quit", on_quit),
    )
    icon = Icon("discord-music-rpc", icon_image, menu=menu)

    tray_thread = threading.Thread(target=icon.run, daemon=True)
    tray_thread.start()

    return icon
