import gevent
import gevent.monkey

gevent.monkey.patch_all(thread=False)

import contextlib
import logging
import os
import shutil
import socket
import tempfile
import time
from datetime import datetime
from pathlib import Path

import ffmpeg
from tqdm import tqdm

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("videoshare")
fh = logging.FileHandler(f"videoshare.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s | %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


@contextlib.contextmanager
def _tmpdir_scope():
    tmpdir = tempfile.mkdtemp()
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)


def _do_watch_progress(filename, sock, handler):
    """Function to run in a separate gevent greenlet to read progress
    events from a unix-domain socket."""
    connection, client_address = sock.accept()
    data = b""
    try:
        while True:
            more_data = connection.recv(16)
            if not more_data:
                break
            data += more_data
            lines = data.split(b"\n")
            for line in lines[:-1]:
                line = line.decode()
                parts = line.split("=")
                key = parts[0] if len(parts) > 0 else None
                value = parts[1] if len(parts) > 1 else None
                handler(key, value)
            data = lines[-1]
    finally:
        connection.close()


@contextlib.contextmanager
def _watch_progress(handler):
    """Context manager for creating a unix-domain socket and listen for
    ffmpeg progress events.

    The socket filename is yielded from the context manager and the
    socket is closed when the context manager is exited.

    Args:
        handler: a function to be called when progress events are
            received; receives a ``key`` argument and ``value``
            argument. (The example ``show_progress`` below uses tqdm)

    Yields:
        socket_filename: the name of the socket file.
    """
    with _tmpdir_scope() as tmpdir:
        socket_filename = os.path.join(tmpdir, "sock")
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        with contextlib.closing(sock):
            sock.bind(socket_filename)
            sock.listen(1)
            child = gevent.spawn(_do_watch_progress, socket_filename, sock, handler)
            try:
                yield socket_filename
            except:
                gevent.kill(child)
                raise


@contextlib.contextmanager
def show_progress(total_duration):
    """Create a unix-domain socket to watch progress and render tqdm
    progress bar."""
    with tqdm(total=round(total_duration, 2)) as bar:

        def handler(key, value):
            if key == "out_time_ms":
                time = round(float(value) / 1000000.0, 2)
                bar.update(time - bar.n)
            elif key == "progress" and value == "end":
                bar.update(bar.total - bar.n)

        with _watch_progress(handler) as socket_filename:
            yield socket_filename


def convertWithProgress(input, output, mode="iphone"):
    """
    compress videos for a particular purpose.
    mode=iphone, save file as .mov, 1920x1080, crf=28
    mode=storage, save file as .mp4, 4K, crf=24, codec=libx264
    mode=anything else, save file as .mp4, 4K, crf=28, codec=libx265
    """
    total_duration = float(ffmpeg.probe(input)["format"]["duration"])
    size = os.path.getsize(input) / 1000 / 1000
    logger.info(f"Start compress file {input}, Size {size:.2f} MB")
    t = time.time()
    with show_progress(total_duration) as socket_filename:
        # See https://ffmpeg.org/ffmpeg-filters.html#Examples-44
        try:
            if mode == "iphone":
                # ffmpeg -i input.mp4 -vf scale=1920:1080 -crf 28 output.mov
                task = ffmpeg.input(input).output(output, crf=28, vf="scale=1920:1080")
            elif mode == "storage":
                # libx264 is able to do live preview on mac and crf24 gives almost no quality loss, and ~ 50% size.
                task = ffmpeg.input(input).output(output, vcodec="libx264", crf=24)
            elif mode == "test":
                # ffmpeg -i input.mp4 -vcodec libx265 -crf 28 output.mp4
                # task = ffmpeg.input(input).output(output, crf=28, vcodec='libx265')
                # libx264 is able to do live preview on mac and crf24 gives almost no quality loss, and ~ 50% size.
                task = ffmpeg.input(input).output(
                    output, vcodec="libx264", crf=24, **{"c:v": "h264_videotoolbox"}
                )
            else:
                # ffmpeg -i input.mp4 -vcodec libx265 -crf 28 output.mp4
                task = ffmpeg.input(input).output(output, crf=28, vcodec="libx265")
            (
                task.global_args("-progress", f"unix://{socket_filename}")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            logger.info(f"Finish compress file {input} in {(time.time()-t)/60:.2f} minutes")
            return 0
        except ffmpeg.Error as e:
            logger.error(f"Error : {e.stderr}")
            return 1


def compressVideos(files, mode="iphone"):
    """
    compress videos for a particular purpose.
    mode=iphone, save file as .mov, 1920x1080, crf=28
    mode=storage, save file as .mp4, 4K, crf=28, codec=libx265
    """
    logger.info(f"Find {len(files)} videos to compress.")
    compressed = []
    for file in files:
        folder = Path(file).parent / mode
        folder.mkdir(parents=True, exist_ok=True)
        suffix = ".MOV" if mode == "iphone" else ".MP4"
        output = folder / (Path(file).stem + suffix)
        convertWithProgress(file, str(output), mode)
        compressed.append(str(output))
    return compressed


def uploadVideos(files):
    from bypy import ByPy

    by = ByPy()
    d = datetime.now().strftime("%Y_%m_%d_videos")
    logger.info(f"Find {len(files)} files to upload")
    for file in files:
        try:
            name = Path(file).name
            size = os.path.getsize(file) / 1000 / 1000
            logger.info(f"Start upload file : {name}, Size {size:.2f} MB")
            t0 = time.time()
            by.upload(file, f"{d}/{name}", ondup="newcopy")
            dt = time.time() - t0
            logger.info(f"Finished upload file in {dt/60:.2f} minutes")
        except Exception as e:
            logger.error(f"!!!!Upload file error: {e}")


if __name__ == "__main__":
    file = "./test.mp4"
    compressVideos([file], mode="test")
