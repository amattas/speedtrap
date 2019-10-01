import logging
import cv2
import threading
import time
import uuid
import cloudstorage



class VideoRecorder:

    def __init__(self, config, recording=False, speed=0):
        self.logger = logging.getLogger('SpeedTrap')
        self.logger.debug("Creating VideoRecorder() instance")
        self._recording = recording
        self._speed = speed
        self._config = config
        self._load_config(config)

    def _load_config(self, config):
        self.logger.debug("Entering _load_config()")
        self._xresolution = int(config['CAMERA']['XResolution'])
        self._yresolution = int(config['CAMERA']['YResolution'])
        self._frame_rate = int(config['CAMERA']['FrameRate'])
        self._file_extension = config['CAMERA']['FileExtension']
        self._fourcc_video_codec = config['CAMERA']['FourCCVideoCodec']
        self._storage_path = config['STORAGE']['StoragePath']
        self._storage_type = config['STORAGE']['StorageType']
        self.logger.debug("Leaving _load_config()")

    def start_recording(self):
        self.logger.debug("Entering start_recording()")
        self._recording = True
        if not hasattr(self, '_recording_thread'):
            self._start_recording_thread()
        elif not self._recording_thread.is_alive():
            self._start_recording_thread()
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
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._xresolution)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._yresolution)
        video_codec = cv2.VideoWriter_fourcc(*self._fourcc_video_codec)
        video_filename = str(uuid.uuid4().hex) + self._file_extension
        self.logger.debug("Writing file %s", video_filename)
        video_writer = cv2.VideoWriter(self._storage_path+video_filename, video_codec, self._frame_rate,
                                       (self._xresolution, self._yresolution))
        while self._recording:
            ret, frame = video_capture.read()
            self._video_overlay(frame)
            self.logger.debug('Shape of source frame is %s', frame.shape)
            video_writer.write(frame)
        if not self._storage_type == 'LocalOnly':
            cs = cloudstorage.CloudStorage(self._config)
            cs.store_cloud_image(video_filename)
        video_capture.release()
        video_writer.release()
        cv2.destroyAllWindows()
        self.logger.debug("Leaving video_recorder()")

    def _video_overlay(self, img):
        overlay_text = '{0!s} mph     {1!s}'.format(self._speed, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        self.logger.debug("Video overlay text %s", overlay_text)
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = .8
        font_thickness = 2
        color = (0, 0, 255)
        # text_size = cv2.getTextSize(overlay_text,font_face, font_scale, font_thickness)
        cv2.putText(img, overlay_text, (20, self._yresolution-20), font_face, font_scale, color,
                    font_thickness, cv2.LINE_AA)
