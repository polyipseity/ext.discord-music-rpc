import os

from PIL import Image
from pystray import Icon, Menu, MenuItem

from . import killer
from .sources import TrackWithSource


def on_quit(icon, item):
    killer.exit_gracefully()
    icon.stop()


def update_tray(icon, track: TrackWithSource | None):
    menu_items = [
        MenuItem("Discord Music RPC", lambda icon, item: None, enabled=False),
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
        MenuItem("Quit", on_quit),
    )

    icon = Icon("discord-music-rpc", icon_image, menu=menu)

    icon.run_detached()  # todo: fix on mac

    return icon
