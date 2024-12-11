import time

import pypresence

from . import killer, logger
from .config import load_config
from .discord_rpc import DiscordRichPresence
from .sources import MusicSourceManager
from .tray import run_tray_icon, update_tray
from .utils import is_same_track

MAIN_SLEEP_SEC = 1


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
    icon = run_tray_icon()

    config = None

    while not killer.kill_now:
        try:
            config, _config_updated = get_config(config)

            music_sources = MusicSourceManager(config)
            discord_rpc = DiscordRichPresence(config)

            try:
                logger.debug("Connecting to RPC")
                discord_rpc.connect()
                logger.debug("Connected to RPC")

                last_track = None

                while not killer.kill_now:
                    _config, config_updated = get_config(config)
                    if config_updated:
                        logger.info("Config updated, reloading")
                        break

                    current_track = music_sources.get_current_track()

                    if current_track:
                        if not is_same_track(current_track, last_track):
                            logger.info(
                                f"Now playing: {current_track.track.artist} - {current_track.track.name} ({current_track.source})"
                            )

                        discord_rpc.update(current_track)
                    else:
                        if not is_same_track(current_track, last_track):
                            logger.info("Stopped playing")

                        discord_rpc.clear()

                    update_tray(icon, current_track)

                    last_track = current_track

                    time.sleep(MAIN_SLEEP_SEC)
            except pypresence.exceptions.PipeClosed:
                logger.warning("Lost connection to Discord, attempting to reconnect...")
                time.sleep(1)
            except pypresence.exceptions.DiscordNotFound:
                logger.warning("Couldn't find Discord, is it open? Trying again...")
                time.sleep(3)
            except pypresence.exceptions.DiscordError as e:
                logger.warning(e)
                time.sleep(1)

            discord_rpc.close()
            logger.debug("Closed Discord RPC")

            music_sources.stop()
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            time.sleep(5)

    icon.stop()


if __name__ == "__main__":
    main()
