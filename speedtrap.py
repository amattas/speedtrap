import configparser
import logging
import time
import threading
import json
import signal
from localtools import LocalTools
from configuration import Configuration
from logspeed import LogSpeed
from radar import Radar

def main():
    config = Configuration("config.ini")
    logging.basicConfig(level=config.logging_level)
    logger = logging.getLogger('SpeedTrap')
    logger.info("SpeedTrap Starting")
    logger.info("Loading configuration file")
    if config.clear_local_on_start:
        LocalTools.clean_local(config)
    log_speed = LogSpeed(config)

    radar = Radar(config)
    execute_loop = True
    while execute_loop:
        try:
            current_report = radar.read_serial_buffer()
            if (len(current_report) > 0):
                try:
                    current_report_json = json.loads(current_report)
                    current_speed = abs(float(current_report_json['speed']))
                    logger.debug("Current speed is %s", current_speed)
                    log_speed.log_speed(current_speed)
                except:
                    pass
            else:
                log_speed.log_speed(0)
        except KeyboardInterrupt:
            execute_loop = False
    logger.info("SpeedTrap Terminating")
    while threading.active_count() > 1:
        logger.info('Waiting for %s threads to terminate.', threading.active_count()-1)
        time.sleep(1)

def receiveSignal(signalNumber, frame):
    if signalNumber == signal.SIGQUIT:
        execute_loop = False
    return

if __name__ == '__main__':
    signal.signal(signal.SIGQUIT, receiveSignal)
    main()
