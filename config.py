import pathlib


class ExternalVolume:
    folders = [
        pathlib.Path("/Volumes/Untitled"),
        pathlib.Path("/Volumes/SD_Card"),
    ]


class SaveFolder:
    images: str = "/Volumes/store/Pictures"
    videos: str = "/Volumes/store/Videos"
