import time

import pypresence
from .config import Config
from .sources.sources import MusicSourceManager
from .discord_rpc import DiscordRichPresence
from .utils import is_same_track


def main():
    config = Config()
    config.validate()

    music_sources = MusicSourceManager(config)
    discord_rpc = DiscordRichPresence(config)

    while True:
        try:
            # Connect to Discord RPC
            discord_rpc.connect()

            last_track = None

            while True:
                current_track = music_sources.get_current_track()

                if not is_same_track(current_track, last_track):
                    print(
                        f"Now playing: {current_track.artist} - {current_track.name} ({current_track.source})"
                    )

                discord_rpc.update(current_track)

                last_track = current_track

                time.sleep(
                    1
                )  # todo: config this? diff services diff sleeps? (ratelimiting)

        except KeyboardInterrupt:
            print("\nStopping RPC...")
            break
        except pypresence.exceptions.PipeClosed:
            print("Lost connection to Discord, attempting to reconnect...")
            time.sleep(1)
        except pypresence.exceptions.DiscordNotFound:
            print("Couldn't find Discord, is it open? Trying again...")
            time.sleep(3)
        except pypresence.exceptions.DiscordError as e:
            print(e)
            time.sleep(1)

    discord_rpc.close()


if __name__ == "__main__":
    main()
