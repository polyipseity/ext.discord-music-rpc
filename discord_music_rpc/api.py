import json

from pydantic import TypeAdapter
from websockets.sync.server import ServerConnection, serve

from . import logger
from .sources import TrackWithSource


class Api:
    current_track: TrackWithSource | None = None

    def __init__(self, host="localhost", port=47474):
        self.host = host
        self.port = port
        self.clients = set()
        self.current_track = None

    def handle_client(self, conn: ServerConnection) -> None:
        self.clients.add(conn)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")

        try:
            while True:
                message = conn.recv()

                try:
                    track_json = json.loads(message)

                    logger.debug(track_json)

                    match track_json["type"]:
                        case "track_update":
                            if not track_json["data"]:
                                self.current_track = None
                            else:
                                self.current_track = TypeAdapter(
                                    TrackWithSource
                                ).validate_python(
                                    {
                                        "track": track_json["data"],
                                        "source": track_json["source"],
                                        "source_image": track_json["source_image"],
                                    }
                                )

                            logger.debug(f"Received track: {self.current_track}")
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Client connection error: {e}")
        finally:
            self.clients.remove(conn)
            conn.close()
            logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    def start(self):
        try:
            with serve(self.handle_client, self.host, self.port) as server:
                logger.info(f"WebSocket server started on {self.host}:{self.port}")
                # Block until server is stopped
                server.serve_forever()
        except Exception as e:
            logger.error(f"Server start error: {e}")

    def get_current_track(self) -> TrackWithSource | None:
        return self.current_track
