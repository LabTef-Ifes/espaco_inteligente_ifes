import os, re, sys
from subprocess import Popen, PIPE, STDOUT
from utils import load_options
from is_wire.core import Logger

"""summary
"""
def get_person_gesture(folder):
    """???

    Args:
        folder (str): _description_

    Returns:
        Tuple[int]: (person_id,gesture_id). Ex :(1,1) for p001g01
    """
    match = re.search(r'p(\d+)g(\d+)', folder)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


log = Logger(name='MakeVideos')
options = load_options(print_options=False)

if not os.path.exists(options.folder):
    log.critical("Folder '{}' doesn't exist", options.folder)
    sys.exit(-1)

# ???
ffmpeg_base_command = "ffmpeg -y -r {fps:.1f} -start_number 0 -i {file_pattern:s} -c:v libx264 -vf fps={fps:.1f} -vf " \
                      "format=rgb24 {video_file:s} "

for root, dirs, files in os.walk(options.folder):
    for exp_folder in dirs:
        person_id, gesture_id = get_person_gesture(exp_folder)
        if person_id is None or gesture_id is None:
            continue
         
        sequence_folder = os.path.join(options.folder, exp_folder)
        for camera in options.cameras:
            file_pattern = os.path.join(
                sequence_folder,
                'c{camera_id:02d}s%08d.jpeg'.format(camera_id=camera.id))
            video_file = os.path.join(
                options.folder, 'p{:03d}g{:02d}c{:02d}.mp4'.format(
                    person_id, gesture_id, camera.id))
            if os.path.exists(video_file):
                log.info("Video '{}' already exists", video_file)
                continue
            ffmpeg_command = ffmpeg_base_command.format(
                fps=camera.config.sampling.frequency.value,
                file_pattern=file_pattern,
                video_file=video_file)
            
            log.info("Creating video '{}'", video_file)
            process = Popen(ffmpeg_command.split(), stdout=PIPE, stderr=STDOUT)

            if process.wait() == 0:
                log.info("Done")
            else:
                log.warn("\'{}\' failed", video_file)
    # only first folder level
    break
