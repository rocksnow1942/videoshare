import gevent
import gevent.monkey
gevent.monkey.patch_all(thread=False)
from bypy import ByPy
import glob
import shutil
from pathlib import Path
from datetime import datetime
import time
import os
from tqdm import tqdm
import contextlib
import ffmpeg
import socket
import tempfile
import logging
import argparse


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('videoshare')
fh = logging.FileHandler(f'videoshare.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s - %(message)s')
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
    data = b''
    try:
        while True:
            more_data = connection.recv(16)
            if not more_data:
                break
            data += more_data
            lines = data.split(b'\n')
            for line in lines[:-1]:
                line = line.decode()
                parts = line.split('=')
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
        socket_filename = os.path.join(tmpdir, 'sock')
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
            if key == 'out_time_ms':
                time = round(float(value) / 1000000., 2)
                bar.update(time - bar.n)
            elif key == 'progress' and value == 'end':
                bar.update(bar.total - bar.n)
        with _watch_progress(handler) as socket_filename:
            yield socket_filename


def convertWithProgress(input,output,crf=28):        
    total_duration = float(ffmpeg.probe(input)['format']['duration'])
    size = os.path.getsize(input)/1000/1000
    logger.info(f"Start compress file {input}, Size {size:.2f} MB")
    t = time.time()
    with show_progress(total_duration) as socket_filename:
        # See https://ffmpeg.org/ffmpeg-filters.html#Examples-44        
        try:
            (
            # this equals to 
            # ffmpeg -i input.mp4 -vcodec libx265 -crf 28 output.mp4
            ffmpeg
                .input(input)
                .output(output, crf=crf, vcodec='libx265')
                .global_args('-progress', 'unix://{}'.format(socket_filename))                
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            logger.info(f"Finish compress file {input} in {(time.time()-t)/60:.2f} minutes")
            return 0
        except ffmpeg.Error as e:            
            logger.error(f"Error : {e.stderr}")
            return 1

def compressVideos(files,crf=28):
    logger.info(f"Find {len(files)} videos to compress.")
    compressed = []
    for file in files:
        folder = Path(file).parent / 'compressed'
        os.mkdir(folder) if not os.path.exists(folder) else None
        output = folder / Path(file).name        
        convertWithProgress(file,str(output),crf)
        compressed.append(str(output))
    return compressed

def uploadVideos(files):    
    by = ByPy()    
    d = datetime.now().strftime('%Y_%m_%d_videos')
    logger.info(f"Find {len(files)} videos to upload")
    for file in files:        
        try:
            name = Path(file).name
            size = os.path.getsize(file)/1000/1000
            logger.info(f"Start upload file : {name}, Size {size:.2f} MB")
            t0 = time.time()
            by.upload(file,f"{d}/{name}",ondup='newcopy')
            dt = time.time() - t0
            logger.info(f"Finished upload file in {dt/60:.2f} minutes")
        except Exception as e:
            logger.error(f"!!!!Upload file error: {e}")
            
            
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
    Compress and upload videos to Baidu Yun in MP4 format.    
    Place videos in ./input folder. Or use -f to specify folder.
    Then the script will compress videos and upload them to Baidu Yun.
    The compressed videos will be moved to ./output folder.
    The uploaded videos will be moved to ./uploaded folder.
    """)
    parser.add_argument('-f', type=str, default='input', help='Folder to look for videos')
    parser.add_argument('-crf', type=int, default=28, help='ffmpeg crf value, 0-51 where 0 is lossless, 23 is default 51 is worst')
    parser.add_argument('-nu','--noupload', nargs='?', const=True, default=False, help='Compress videos Only, no upload')
    args = parser.parse_args()        
    folder = args.f
    videos = glob.glob(f'{folder}/*.[mM]*')
    compressed = compressVideos(videos,args.crf)
    if not args.noupload:
        uploadVideos(compressed)
    
    
        

