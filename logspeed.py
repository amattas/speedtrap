import logging
import time

from videorecorder2 import VideoRecorder2
from datarecorder import DataRecorder

class LogSpeed:

    def __init__(self, config):
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.LogSpeed')
        self.logger.debug("Creating LogSpeed() instance")
        self._current_max = 0
        self._video_recorder = VideoRecorder2(config)
        self._data_recorder = DataRecorder(config)
        self._video_recorder.start_recorder()

    def log_speed(self, speed):
        self.logger.debug("Entering log_speed()")
        if self._current_max == 0 and speed == 0:
            pass
        elif speed >= self._config.log_threshold:
            if speed > self._current_max:
                self.logger.debug("Current maximum speed was %s now %s", self._current_max, speed)
                self._current_max = speed
            if speed >= self._config.record_threshold:
                self.logger.debug("Logging speed %s to video", speed)
                self._video_recorder.start_recording()
        elif speed < self._config.log_threshold:
            file_name = self._video_recorder.stop_recording()
            if self._current_max >= self._config.log_threshold:
                self._data_recorder.record(self._current_max, time.localtime(), file_name)
            self._current_max = 0
            self.logger.debug("Leaving log_speed()")
