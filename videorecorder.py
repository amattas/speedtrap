import logging
import cv2
import threading
import time


class VideoRecorder:

    def __init__(self, recording=False, speed=0):
        self.logger = logging.getLogger('SpeedTrap')
        self.logger.debug("Creating VideoRecorder() instance")
        self._recording = recording
        self._speed = speed

    def start_recording(self):
        self.logger.debug("Entering start_recording()")
        self._recording = True
        if not hasattr(self, '_recording_thread'):
            self._start_recording_thread()
        elif not self._recording_thread.is_alive():
            self._start_recording_thread()
            self.logger.info("Starting recording thread")
        else:
            self.logger.info("Existing recording thread started, using existing")
        self.logger.debug("Leaving start_recording()")

    def _start_recording_thread(self):
        self.logger.debug("Entering start_recording_thread()")
        self._recording_thread = threading.Thread(target=self._video_recorder)
        self._recording_thread.start()
        self.logger.debug("Leaving start_recording_thread()")

    def stop_recording(self):
        self.logger.debug("Entering stop_recording()")
        self._recording = False
        self.logger.debug("Leaving stop_recording()")

    def set_speed(self, speed):
        self._speed = speed

    def _video_recorder(self):
        self.logger.debug("Entering video_recorder()")
        video_capture = cv2.VideoCapture(0)
        video_capture.set(3, 1024)
        video_capture.set(4, 768)
        video_codec = cv2.VideoWriter_fourcc(*'MJPG')
        video_writer = cv2.VideoWriter("cam_video.avi", video_codec, 20.0, (1024, 768))
        while self._recording:
            ret, frame = video_capture.read()
            self._video_overlay(frame)
            video_writer.write(frame)
        video_capture.release()
        video_writer.release()
        cv2.destroyAllWindows()
        self.logger.debug("Leaving video_recorder()")

    def _video_overlay(self, img):
        overlay_text = '{0!s} mph     {1!s}'.format(self._speed, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        self.logger.debug("Video overlay text %s", overlay_text)
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        scale = .8
        color = (0, 0, 255)
        cv2.putText(img, overlay_text, (20, 748), font_face, scale, color, 2, cv2.LINE_AA)