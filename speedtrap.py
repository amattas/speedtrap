import logging
import json
import signal
from localtools import LocalTools
from capture import Capture
from record import Record
from configuration import Configuration
from radar import Radar
from multiprocessing import Pipe, Process, Queue


def main():
    config = Configuration("config.ini")
    logging.basicConfig(level=config.logging_level)
    logger = logging.getLogger('SpeedTrap')
    logger.info("SpeedTrap Starting")
    logger.info("Loading configuration file")
    if config.clear_local_on_start:
        LocalTools.clean_local(config)
    # log_speed = LogSpeed(config)
    execute_loop = True
    radar = Radar(config)

    # Create pipes for inter-process communication
    # radar_parent, radar_child = Pipe() - ToDo: separate radar process
    # log_parent, log_child = Pipe() - ToDo: separate logging process
    video_queue = Queue()  # Video Ring Buffer
    capture_parent, capture_mode_child = Pipe()  # Signaling to Camera Process
    capture_speed_parent, capture_speed_child = Pipe()   # Signaling to Camera Process
    record_parent, record_mode_child = Pipe()  # Signaling to Record Process

    capture = Capture(config)
    record = Record(config)

    capture_process = Process(target=capture.capture, args=(capture_mode_child, capture_speed_child,
                                                            video_queue))
    capture_process.start()

    record_process = Process(target=record.record, args=(record_mode_child, video_queue))
    record_process.start()

    # Tracking if we are currently recording so we don't accidentally create a race condition
    recording = False
    speed = 0
    while execute_loop:
        try:
            if record_parent.poll():
                record_result = record_parent.recv()
                # ToDo We aren't recording anymore, so lets log
                # Change the behavior of the capture process back to its default. The recording process already changed
                # itself
                recording = False
                capture_parent.send(0)
            current_report = radar.read_serial_buffer()
            if len(current_report) > 0:
                try:
                    current_report_json = json.loads(current_report)
                    speed = abs(float(current_report_json['speed']))
                except:
                    pass
            else:
                speed = 0
            logger.debug("Current speed is %s", speed)
            capture_speed_parent.send(speed)
            if speed > config.record_threshold and recording is False:
                # ToDo: Eliminate Log Threshold Configuration
                recording = True
                # Change the behavior of the video capture and recording process to record mode
                capture_parent.send(1)
                record_parent.send(1)
            # log_speed.log_speed(current_speed)
        except KeyboardInterrupt:
            execute_loop = False
    logger.info("SpeedTrap Terminating")


# ToDo: Add graceful handling of exists so this can be ran as a daemon
def receive_signal(signal_number, frame):
    if signal_number == signal.SIGQUIT:
        return


if __name__ == '__main__':
    signal.signal(signal.SIGQUIT, receive_signal)
    main()
