### For auto import videos and Images

For SONY A7C camera,

Organize videos and images to target foler, based on it's month and day.

The videos are compressed via ffmpeg and uploaded to Baidu yun for sharing.

* Edit `A7C-import.sh` file, point to the correct `main.py` location.
* Make the `A7C-import.sh` executable with `chmod a+x`.
* Remove th `.sh` so that the script is executed by double clicking.

For making the script execute in a particular folder, see [reference Here](https://stackoverflow.com/questions/5125907/how-to-run-a-shell-script-in-os-x-by-double-clicking).

`config.ini` configures the folders on my computer.

The videos are imported from camera, then compressed and saved to the same folder under `compressed`
