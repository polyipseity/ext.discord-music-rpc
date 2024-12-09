import time
from .config import Config
from .sources.sources import MusicSourceManager
from .discord_rpc import DiscordRichPresence


def main():
    config = Config()
    config.validate()

    music_sources = MusicSourceManager(config)
    discord_rpc = DiscordRichPresence(config)

    try:
        # Connect to Discord RPC
        discord_rpc.connect()

        last_track = None

        while True:
            current_track = music_sources.get_current_track()

            if not last_track or (
                current_track.name != last_track.name
                and current_track.artist != last_track.artist
                and current_track.source != last_track.source
            ):
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
    finally:
        discord_rpc.close()


if __name__ == "__main__":
    main()
