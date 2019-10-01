import logging
import time

from videorecorder import VideoRecorder
from datarecorder import DataRecorder


class LogSpeed:

    def __init__(self, config):
        self.logger = logging.getLogger('SpeedTrap')
        self.logger.debug("Creating LogSpeed() instance")
        self._load_config(config)
        self._current_max = 0
        self._video_recorder = VideoRecorder(config)
        self._data_recorder = DataRecorder(config)

    def _load_config(self, config):
        self.logger.debug("Entering _load_config()")
        self._log_threshold = int(config['DEFAULT']['LogThreshold'])
        self._record_threshold = int(config['DEFAULT']['RecordThreshold'])
        self.logger.debug("Leaving _load_config()")

    def log_speed(self, speed):
        self.logger.debug("Entering log_speed()")
        if speed >= self._log_threshold:
            if speed > self._current_max:
                self.logger.debug("Current maximum speed was %s now %s", self._current_max, speed)
                self._current_max = speed
            if speed >= self._record_threshold:
                self.logger.debug("Logging speed %s to video", speed)
                self._video_recorder.record_speed(speed)
            elif self._current_max >= self._record_threshold:
                self.logger.debug("Logging speed %s to video",speed)
                self._video_recorder.record_speed(speed)
        elif speed < self._log_threshold:
            if self._current_max >= self._record_threshold:
                self.logger.debug("Stopping video recording")
                self._video_recorder.stop_recording()
            elif self._current_max >= self._log_threshold:
                self.logger.debug("Logging maximum speed")
                self._data_recorder.record(self._current_max, time.localtime(), None)
                return
            self._current_max = 0
        self.logger.debug("Entering log_speed()")
