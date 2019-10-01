import configparser
import logging
import time
import threading

from logspeed import LogSpeed

def main():
    logger.info("SpeedTrap Starting")
    logger.info("Loading configuration file")
    config = configparser.ConfigParser()
    config.read('config.ini')
    if logger.getEffectiveLevel() == logging.DEBUG:
        for s in config.sections():
            logger.debug('Loaded configuration section %s', s)
            for k in config[s]:
                logger.debug('Loaded configration key %s', k)
    logger.info("Configuration file loaded")
    log_speed = LogSpeed(config)
    log_speed.log_speed(25)
    time.sleep(5)
    log_speed.log_speed(35)
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
