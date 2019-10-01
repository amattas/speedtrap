import logging
import threading

from videorecorder import VideoRecorder


class LogSpeed:

    def __init__(self, config):
        self.logger = logging.getLogger('SpeedTrap')
        self.logger.debug("Creating LogSpeed() instance")
        self._load_config(config)
        self._current_max = 0
        self._video_recorder = VideoRecorder(config)

    def _load_config(self, config):
        self._log_threshold = int(config['DEFAULT']['LogThreshold'])
        self._record_threshold = int(config['DEFAULT']['RecordThreshold'])

    def log_speed(self, speed):
        if speed >= self._log_threshold:
            if speed > self._current_max:
                self.logger.debug("Current maximium speed was %s now %s", self._current_max, speed)
                self._current_max = speed
            if speed >= self._record_threshold:
                    self._video_recorder.record_speed(speed)
                    return
        elif speed < self._log_threshold:
            if self._current_max >= self._record_threshold:
                    self._video_recorder.stop_recording()
            elif self._current_max >= self._log_threshold:
                    #  Call Record Max Speed
                    return
            self._current_max = 0

