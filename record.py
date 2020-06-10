import logging
import cv2
import queue
import time

class Record:
    """
    The Record class contains the methods needed to convert camera frames stored on the multiprocessing.Queue()
    to video files using cv2 module. Using the record() function, it is designed to add the overlays to the images
    and store the video files as configured in the configuration file. Additionally when recording is completed
    this function will return information about the recording on the multiprocessing.Pipe()
    """

    def __init__(self, config):
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.Record')
        self.logger.debug("Creating Capture() instance")
        # Create FIFO Queue for storing video frames
        self._current_filename = 'unknown' + self._config.camera_file_extension
        self._video_codec = cv2.VideoWriter_fourcc(*self._config.camera_fourcc_codec)

    def record(self, record_mode_child, video_queue):
        """
        Records video frames stored in a multiprocessing.Queue() to file.

        Records video frames stored in a multiprocessing.Queue() to file using the cv2 module. This method is intended
        to called as its own multiprocessing.Process() and reads frames stored on a multiprocessing.Queue() and writes
        them to storage. It returns an array containing a timestamp, filename, and maximum speed using it's
        multiprocessing.Pipe()

        Parameters
        ----------
        record_mode_child : Pipe()
            This is one half of a bidirectional multiprocessing.Pipe(). It's used to control the behavior of the
            method. Possible values include: -1 which will cause the process to clean-up and exit gracefully, 0
            (the default) which will cause the record process to wait 10ms and then loop, and 1 which will cause the
            record process to begin writing video files. Upon the completion of writing a video file this pipe will
            return the filepath and maximum speed to the parent process.
        video_queue : Queue()
            This FIFO multiprocessing.Queue() is used as a ring buffer for capturing video to. Due to the delay in
            switching a web cam into record mode using a ring buffer is necessary to ensure that the full video stream
            is captured.
        """
        self.logger.debug("Entering record()")
        mode = 0
        filename = None
        max_speed = 0
        # Exit on -1
        while mode != -1:
            if record_mode_child.poll():
                mode = record_mode_child.recv()
            # Record on 1
            if mode == 1:
                if filename is None:
                    filename = str(int(time.time())) + self._config.camera_file_extension
                self.logger.debug("Filename set to: %s", filename)
                self.logger.debug("Video queue is empty: %s", video_queue.empty())
                self.logger.debug("Creating video_writer")
                video_writer = cv2.VideoWriter(self._config.storage_path + filename,
                                               self._video_codec, self._config.camera_framerate,
                                               (self._config.camera_xresolution,
                                                self._config.camera_yresolution))
                # Write frames to file
                while True:
                    try:
                        self.logger.debug("Attempting to pop video from from queue, queue size is roughly %s",
                                          video_queue.qsize())
                        queue_record = video_queue.get(False)
                        self.logger.debug("Successfully read queue item")
                        write_frame = self._overlay(queue_record[0], queue_record[1], queue_record[2])
                        self.logger.debug('Shape of source frame is %s', write_frame.shape)
                        video_writer.write(write_frame)
                        if queue_record[1] > max_speed:
                            max_speed = queue_record[1]
                        # If Max Speed is 0, then nothing has been written yet
                        if queue_record[1] == 0 and max_speed != 0:
                            self.logger.debug("No movement detected, breaking from loop")
                            break
                    except queue.Empty:
                        self.logger.debug("Video queue is empty, breaking from loop")
                        break
                self.logger.debug("Completing video writing")
                video_writer.release()
                # ToDo: Add code to save to cloud
                mode = 0
                record_mode_child.send((self._config.storage_path + filename, max_speed))
                max_speed = 0
            if mode == 0:
                time.sleep(.01)

        self.logger.debug("Leaving recorder()")

    def _overlay(self, frame, speed, recorded_time):
        """
        Private function to add text overlay to video.

        Private function to create an overlay on top of a video frame with the time the frame was recorded and the
        speed.

        Parameters
        ----------
        frame : image
            This is a single frame of a video stream that the overlay text will be applied to
        speed : float
            A decimal number which represents the speed to be overlaid on the frame.
        recorded_time : str
            A string representing the time the frame was recorded to be overlaid on the frame

        Returns
        -------
        image
            Returns an image with the parameter text overlaid
        """
        self.logger.debug("Entering _overlay()")
        overlay_text = '{0!s} mph     {1!s}'.format(speed, recorded_time)
        self.logger.debug("Video overlay text %s", overlay_text)
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = .8
        font_thickness = 2
        color = (0, 0, 255)
        # text_size = cv2.getTextSize(overlay_text,font_face, font_scale, font_thickness)
        # ToDo: Need to fix alignment of text
        new_image = cv2.putText(frame, overlay_text, (20, self._config.camera_yresolution - 20), font_face,
                                font_scale, color,
                                font_thickness, cv2.LINE_AA)
        self.logger.debug("Leaving _overlay()")
        return new_image
