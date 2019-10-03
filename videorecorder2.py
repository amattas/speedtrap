import logging
import cv2
import threading
import time
import uuid
import queue
import cloudstorage


class VideoRecorder2:

    def __init__(self, config):
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.VideoRecorder2')
        self.logger.debug("Creating VideoRecorder2() instance")
        self._config = config
        self._video_recorder_enabled = False
        self._video_recorder_save = False
        self._video_queue = queue.Queue()
        self._speed = 0
        self._current_filename = 'unknown' + self._config.camera_file_extension
        self._video_writer_thread = threading.Thread()
        self._video_reader_thread = threading.Thread()

    def start_recorder(self):
        self.logger.debug("Entering start_recorder()")
        self._video_recorder_enabled = True
        if not self._video_reader_thread.is_alive():
            self.logger.debug("Starting new _video_reader() thread")
            self._video_reader_thread = threading.Thread(target=self._video_reader)
            self._video_reader_thread.start()
        else:
            self.logger.debug("_video_reader() thread already started")
        if not self._video_writer_thread.is_alive():
            self.logger.debug("Starting new _video_writer() thread")
            self._video_writer_thread = threading.Thread(target=self._video_writer)
            self._video_writer_thread.start()
        else:
            self.logger.debug("_video_reader() thread already started")
        self.logger.debug("Leaving start_recorder()")

    def stop_recorder(self):
        self.logger.debug("Entering stop_recorder()")
        self._video_recorder_enabled = False
        self._video_reader_thread.join()
        self._video_writer_thread.join()
        self.logger.debug("Leaving stop_recorder()")

    def _video_reader(self):
        self.logger.debug("Entering _video_reader()")
        video_capture = cv2.VideoCapture(0)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.camera_xresolution)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.camera_yresolution)
        while self._video_recorder_enabled:
            if not self._video_recorder_save:
                video_capture.grab()
            elif self._video_recorder_save:
                ret, frame = video_capture.read()
                if ret:
                    self.logger.debug("Getting video frame and adding to queue")
                    self._video_queue.put((self._current_filename, frame))
                    self.logger.debug("Video queue size roughly %s", self._video_queue.qsize())
        self.logger.debug("Leaving _video_reader()")

    def _video_writer(self):
        self.logger.debug("Entering _video_writer()")
        self._last_filename = None
        self._video_codec = cv2.VideoWriter_fourcc(*self._config.camera_fourcc_codec)
        while self._video_recorder_enabled:
            while self._video_recorder_save:
                self.logger.debug("Recorder Save Enabled: %s, Video queue empty: %s", self._video_recorder_save,
                                  self._video_queue.empty())
                try:
                    self.logger.debug("Attempting to pop video from from queue")
                    _video_queue_record = self._video_queue.get(False)
                    self._video_queue.task_done()
                    self.logger.debug("Received filename %s", _video_queue_record[0])
                    if self._last_filename is None:
                        self._last_filename = _video_queue_record[0]
                        self.logger.debug("New filename is %s", self._last_filename)
                        self._video_writer = cv2.VideoWriter(self._config.storage_path + self._last_filename,
                                                             self._video_codec, self._config.camera_framerate,
                                                             (self._config.camera_xresolution,
                                                              self._config.camera_yresolution))
                    elif not self._last_filename == _video_queue_record[0]:
                        self.logger.debug("New filename is %s", self._last_filename)
                        self._last_filename = _video_queue_record[0]
                        self._video_writer.release()
                        self._video_writer = cv2.VideoWriter(self._config.storage_path + self._last_filename,
                                                             self._video_codec, self._config.camera_framerate,
                                                             (self._config.camera_xresolution, self._config.camera_yresolution))
                    _write_frame = self._video_overlay(_video_queue_record[1])
                    self.logger.debug('Shape of source frame is %s', _write_frame.shape)
                    self._video_writer.write(_write_frame)
                except:
                    self.logger.debug('Entered _video_writer() exception logic')
                    self.logger.debug('*** Last Filename: %s', self._last_filename)
                    if self._last_filename is None:
                        continue
                    self.logger.debug("Video queue empty")
                    self.logger.debug("Completing video writing")
                    self._video_writer.release()
                    if self._config.enable_azure:
                        cloud_storage_file_path = self._config.storage_path + self._last_filename
                        cs = cloudstorage.CloudStorage(self._config)
                        cs.store_cloud_image(cloud_storage_file_path)
                    self._last_filename = None
                    self._video_writer.release()
                    self.logger.debug("Leaving _video_writer()")
                    break
            time.sleep(1)


    def _video_overlay(self, img):
        self.logger.debug("Entering _video_overlay()")
        overlay_text = '{0!s} mph     {1!s}'.format(self._speed,
                                                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        self.logger.debug("Video overlay text %s", overlay_text)
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = .8
        font_thickness = 2
        color = (0, 0, 255)
        # text_size = cv2.getTextSize(overlay_text,font_face, font_scale, font_thickness)
        new_image = cv2.putText(img, overlay_text, (20, self._config.camera_yresolution - 20), font_face,
                                font_scale, color,
                                font_thickness, cv2.LINE_AA)
        self.logger.debug("Leaving _video_overlay()")
        return new_image

    def set_speed(self, speed):
        self.logger.debug("Entering set_speed()")
        self._speed = speed
        self.logger.debug("Leaving set_speed()")

    def start_recording(self, speed=0):
        self.logger.debug("Entering start_recording()")
        self._speed = speed
        self._video_recorder_save = True
        self._current_filename = str(uuid.uuid4().hex) + self._config.camera_file_extension
        self.logger.debug("Leaving start_recording()")
        return self._current_filename

    def stop_recording(self):
        self.logger.debug("Entering stop_recording()")
        current_filename = self._current_filename
        self._video_recorder_save = False
        self.logger.debug("Leaving stop_recording()")





