import json

from pydantic import TypeAdapter
from websockets.sync.server import ServerConnection, serve

from . import logger
from .sources import TrackWithSource


class Api:
    current_tracks: dict[ServerConnection, TrackWithSource] = {}

    def __init__(self, tracker, host="localhost", port=47474):
        self.tracker = tracker
        self.host = host
        self.port = port
        self.clients = set()
        self.current_tracks = {}

    def handle_client(self, conn: ServerConnection) -> None:
        self.clients.add(conn)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")

        try:
            while True:
                message = conn.recv()

                try:
                    track_json = json.loads(message)
                    logger.debug(track_json)

                    config = self.tracker.config

                    match track_json["type"]:
                        case "track_update":
                            track_data = track_json["data"]
                            source = track_json["source"]
                            source_image = track_json["source_image"]

                            source_config = config.for_source(
                                source
                            )  # todo: send config on connection and config change to clients so they dont send the data in the first place. doesnt really matter but would be nice

                            if (
                                not track_data
                                or not source_config
                                or not source_config.enabled
                            ):
                                self.current_tracks.pop(conn, None)
                            else:
                                validated_track = TypeAdapter(
                                    TrackWithSource
                                ).validate_python(
                                    {
                                        "track": track_data,
                                        "source": source,
                                        "source_image": source_image,
                                    }
                                )
                                self.current_tracks[conn] = validated_track

                            logger.debug(f"Current tracks: {self.current_tracks}")

                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Client connection error: {e}")
        finally:
            self.current_tracks.pop(conn, None)
            self.clients.remove(conn)
            conn.close()
            logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    def start(self):
        try:
            with serve(self.handle_client, self.host, self.port) as server:
                logger.info(f"WebSocket server started on {self.host}:{self.port}")
                server.serve_forever()
        except Exception as e:
            logger.error(f"Server start error: {e}")

    def get_current_tracks(self) -> list[TrackWithSource]:
        return list(self.current_tracks.values())
