import threading
import time

import pypresence

from . import killer, logger
from .api import Api
from .config import load_config
from .discord_rpc import DiscordRichPresence
from .sources import MusicSourceManager
from .tray import run_tray_icon


class MusicTracker:
    MAIN_SLEEP_SEC = 1

    def __init__(self):
        self.api = Api(self)
        self.icon = None
        self.discord_rpc = None
        self.music_sources = None
        self.config = None

    def run(self):
        # start api in a separate thread
        threading.Thread(target=self.api.start, daemon=True).start()

        # initialise tray icon
        self.icon = run_tray_icon()

        self.config = None

        while not killer.kill_now:
            try:
                self.config, _config_updated = get_config(self.config)

                self.music_sources = MusicSourceManager(self.config)
                self.discord_rpc = DiscordRichPresence(self.config)

                try:
                    logger.debug("Connecting to RPC")
                    self.discord_rpc.connect()
                    logger.debug("Connected to RPC")

                    while not killer.kill_now:
                        _config, config_updated = get_config(self.config)
                        if config_updated:
                            logger.info("Config updated, reloading")
                            break

                        current_tracks = [
                            *self.api.get_current_tracks(),
                            *self.music_sources.get_current_tracks(),
                        ]

                        self.discord_rpc.update(
                            [track for track in current_tracks if track]
                        )

                        # update_tray(self.icon, current_track) todo: fix

                        time.sleep(self.MAIN_SLEEP_SEC)
                except pypresence.exceptions.PipeClosed:
                    logger.warning(
                        "Lost connection to Discord, attempting to reconnect..."
                    )
                    time.sleep(1)
                except pypresence.exceptions.DiscordNotFound:
                    logger.warning("Couldn't find Discord, is it open? Trying again...")
                    time.sleep(3)
                except pypresence.exceptions.DiscordError as e:
                    logger.warning(e)
                    time.sleep(1)

                self.discord_rpc.close()
                logger.debug("Closed Discord RPC")

                self.music_sources.stop()
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(5)

        self.icon.stop()


def get_config(current_config=None):
    while True:
        config = load_config()

        if config == current_config:
            return config, False

        if not config.validate():
            logger.info("Config failed to validate")
            time.sleep(5)
            continue

        return config, True


def main():
    tracker = MusicTracker()
    tracker.run()


if __name__ == "__main__":
    main()
