import pathlib


class ExternalVolume:
    folders = [
        pathlib.Path("/Volumes/Untitled"),
        pathlib.Path("/Volumes/SD_Card"),
    ]


class SaveFolder:
    images: pathlib.Path = pathlib.Path("/Volumes/store/Photos")
    videos: pathlib.Path = pathlib.Path("/Volumes/store/Videos")
