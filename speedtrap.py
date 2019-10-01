import configparser
import logging
import time
import threading
import json
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
    while True:
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
    logger.info("SpeedTrap Terminating")
    while threading.active_count() > 1:
        logger.info('Waiting for %s threads to terminate.', threading.active_count()-1)
        time.sleep(1)


if __name__ == '__main__':
    main()
