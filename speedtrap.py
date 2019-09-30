import configparser
import logging
import time
import threading
from videorecorder import VideoRecorder

speeding = True


def main():
    logger.info("SpeedTrap Starting")
    video_recorder = VideoRecorder()
    video_recorder.set_speed(25)
    video_recorder.start_recording()
    time.sleep(5)
    video_recorder.stop_recording()
    logger.info("SpeedTrap Terminating")
    while threading.active_count() > 1:
        logger.info('Waiting for %s threads to terminate.', threading.active_count()-1)
        time.sleep(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('SpeedTrap')
    main()
