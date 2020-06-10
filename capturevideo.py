import logging
import cv2
import time

class CaptureVideo:
    """
    The Capture class contains the methods needed to read images frames off of a connected web cam
    using cv2 module. Using the capture() method, it is designed to store the images into a shared
    multiprocessing.Queue(). The capture() method is to be called in its own multiprocessing.Process()
    """

    def __init__(self, config):
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.Capture')
        self.logger.debug("Creating CaptureVideo() instance")
        self._config = config

    def capture(self, capture_child, capture_speed_child, video_queue):
        """
        Captures video frames from a connected web cam.

        Captures video frames from a connected web cam using the cv2 module. This method is intended
        to called as its own multiprocessing.Process() and uses a multiprocessing.Queue() to store captured video
        frames. This method also utilizes multiprocessing.Pipe() to control its behavior.

        Parameters
        ----------
        capture_child : Pipe
            This is one half of a bidirectional multiprocessing.Pipe(). It's used to control the behavior of the
            method. Possible values include: -1 which will cause the process to clean-up and exit gracefully, 0
            (the default) which will cause the capture process to store video in a ring buffer until its maximum size is
            reached, and 1 which will cause the capture process to store video in a ring buffer without enforcing a
            maximum size (to prevent a race condition during recording)
        capture_speed_child : Pipe
            This is one half of a bidirectional  multiprocessing.Pipe(). It is used to log the current speed to be
            imprinted on the video frames.
        video_queue : Queue()
            This FIFO multiprocessing.Queue() is used as a ring buffer for capturing video to. Due to the delay in
            switching a web cam into record mode using a ring buffer is necessary to ensure that the full video stream
            is captured.
        -----
        """
        self.logger.debug("Entering capture()")
        time.sleep(1)
        mode = 0
        speed = 0.
        video_capture = cv2.VideoCapture(0)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.camera_xresolution)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.camera_yresolution)
        while mode != -1:
            if capture_child.poll():
                mode = capture_child.recv()
            if capture_speed_child.poll():
                speed = capture_speed_child.recv()
            ret, frame = video_capture.read()
            if ret:
                self.logger.debug("Getting video frame and adding to queue")
                video_queue.put((frame, speed, time.localtime()))
                self.logger.debug("Video queue size roughly %s", video_queue.qsize())
            # ToDo: Set buffer ring max size as a configuration value
            if mode == 0:
                while video_queue.qsize() > 50:
                    self.logger.debug("Draining ring buffer size roughly %s", video_queue.qsize())
                    video_queue.get(False)
        self.logger.debug("Leaving capture()")
        return
