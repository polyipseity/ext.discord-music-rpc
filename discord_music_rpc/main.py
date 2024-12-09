import time
from .config import Config
from .music_sources import MusicSourceManager
from .discord_rpc import DiscordRichPresence


def main():
    # Validate configuration
    Config.validate()  # todo return some value

    # Initialize components
    config = Config()
    music_sources = MusicSourceManager(config)
    discord_rpc = DiscordRichPresence(config)

    try:
        # Connect to Discord RPC
        discord_rpc.connect()

        # Main application loop
        while True:
            current_track = music_sources.get_current_track()
            print(current_track)

            discord_rpc.update(current_track)

            time.sleep(
                1
            )  # todo: config this? diff services diff sleeps? (ratelimiting)

    except KeyboardInterrupt:
        print("\nStopping RPC...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        discord_rpc.close()


if __name__ == "__main__":
    main()
