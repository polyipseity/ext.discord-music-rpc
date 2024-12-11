import yaml

from .sources import TrackWithSource


def is_same_track(
    track1: TrackWithSource | None, track2: TrackWithSource | None
) -> bool:
    if not track1 and not track2:
        return True

    if not track1 or not track2:
        return False

    return (
        track1.track.name == track2.track.name
        and track1.track.artist == track2.track.artist
        and track1.track.album == track2.track.album
        and track1.source == track2.source
    )


class PrettyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)
