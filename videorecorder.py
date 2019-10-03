import logging
import cv2
import threading
import time
import uuid
import cloudstorage
import queue

from datarecorder import DataRecorder

class VideoRecorder:

    def __init__(self, config):
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.VideoRecorder')
        self.logger.debug("Creating VideoRecorder() instance")
        self._recording = False
        self._speed = 0
        self._current_max = 0
        self._data_recorder = DataRecorder(config)
        self._write_queue = queue.Queue()
        self._write_queue_empty = True

    def record_speed(self, speed):
        self.logger.debug("Entering record_speed()")
        self.logger.debug("Setting speed to %s", speed)
        self._speed = speed
        if speed > self._current_max:
                self.logger.debug("Current maximum speed was %s now %s", self._current_max, speed)
                self._current_max = speed
        if not self._recording:
            self._recording = True
            if not hasattr(self, '_recording_thread'):
                self.logger.debug("Thread not found, starting new recording thread")
                self._start_recording_thread()
            elif not self._recording_thread.is_alive():
                self.logger.debug("Thread not alive, starting new recording thread")
                self._start_recording_thread()

    def _start_recording_thread(self):
        self.logger.debug("Entering start_recording_thread()")
        self._recording_thread = threading.Thread(target=self._video_recorder)
        self._recording_thread.start()
        self._saver_thread = threading.Thread(target=self._video_saver)
        self._saver_thread.start()
        # Make sure recording thread has started
        while not hasattr(self, '_current_video_filename'):
            self.logger.debug("Waiting for recording thread to start")
            continue
        self.logger.debug("Leaving start_recording_thread()")

    def stop_recording(self):
        self.logger.debug("Entering stop_recording()")
        self._recording = False
        while not self._write_queue_empty:
            self.logger.debug("Waiting for video queue to drain")
            self.logger.debug("Video queue size roughly %s", self._write_queue.qsize())
            pass
        if self._config.enable_azure:
            self._data_recorder.record(self._current_max,time.localtime(),self._config.azure_storage_uri_prefix
                                       + self._current_video_filename)
        else:
            self._data_recorder.record(self._current_max,time.localtime(),self._config.storage_path
                                       + self._current_video_filename)
        self._current_max = 0
        self.logger.debug("Leaving stop_recording()")

    def _video_recorder(self):
        self.logger.debug("Entering video_recorder()")
        self._current_video_filename = str(uuid.uuid4().hex) + self._config.camera_file_extension
        video_capture = cv2.VideoCapture(0)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.camera_xresolution)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.camera_yresolution)
        video_codec = cv2.VideoWriter_fourcc(*self._config.camera_fourcc_codec)
        self.logger.debug("Writing file %s", self._current_video_filename)
        self._video_writer = cv2.VideoWriter(self._config.storage_path+self._current_video_filename, video_codec,
                                       self._config.camera_framerate,
                                       (self._config.camera_xresolution, self._config.camera_yresolution))
        while self._recording:
            ret, frame = video_capture.read()
            if ret:
                self.logger.debug("Putting video frame on queue.")
                self._write_queue_empty = False
                self._write_queue.put(frame)
                self.logger.debug("Video queue size roughly %s", self._write_queue.qsize())

            #self._video_overlay(frame)
            #self.logger.debug('Shape of source frame is %s', frame.shape)
            #video_writer.write(frame)
        if self._config.enable_azure:
            cs = cloudstorage.CloudStorage(self._config)
            cs.store_cloud_image(self._current_video_filename)
        # Call logging function
        video_capture.release()
        self._video_writer.release()
        cv2.destroyAllWindows()
        self.logger.debug("Leaving video_recorder()")

    def _video_saver(self):
        self.logger.debug("Entering _video_saver()")
        while self._recording:
            self.logger.debug("Video saver detected recording")
            while not self:
                self.logger.debug("Video saver checking queue")
                try:
                    self.logger.debug("Popping video from from queue")
                    frame = self._write_queue.get()
                    self._write_queue.task_done()
                    self.logger.debug("Video queue size roughly %s", self._write_queue.qsize())
                    self._video_overlay(frame)
                    self.logger.debug('Shape of source frame is %s', frame.shape)
                    self._video_writer.write(frame)
                except queue.Empty:
                    self.logger.debug("Video queue empty")
                    self._write_queue_empty = True
        self.logger.debug("Leaving _video_saver()")

    def _video_overlay(self, img):
        overlay_text = '{0!s} mph     {1!s}'.format(self._speed, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        self.logger.debug("Video overlay text %s", overlay_text)
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = .8
        font_thickness = 2
        color = (0, 0, 255)
        # text_size = cv2.getTextSize(overlay_text,font_face, font_scale, font_thickness)
        cv2.putText(img, overlay_text, (20, self._config.camera_yresolution-20), font_face, font_scale, color,
                    font_thickness, cv2.LINE_AA)
