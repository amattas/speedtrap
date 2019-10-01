import configparser
import logging
import time
import threading

from configuration import Configuration
from logspeed import LogSpeed

def main():
    logger.info("SpeedTrap Starting")
    logger.info("Loading configuration file")
    config = Configuration("config.ini")
    log_speed = LogSpeed(config)
    log_speed.log_speed(25)
    time.sleep(5)
    log_speed.log_speed(26)
    time.sleep(5)
    log_speed.log_speed(24)
    time.sleep(5)
    log_speed.log_speed(25)
    time.sleep(5)
    log_speed.log_speed(30)
    time.sleep(5)
    log_speed.log_speed(26)
    time.sleep(5)
    log_speed.log_speed(20)
    logger.info("SpeedTrap Terminating")
    while threading.active_count() > 1:
        logger.info('Waiting for %s threads to terminate.', threading.active_count()-1)
        time.sleep(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('SpeedTrap')
    main()
