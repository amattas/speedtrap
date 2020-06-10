import os
import logging


class LocalTools:

    def __init__(self, config):
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.LocalTools')

    @staticmethod
    def clean_local(config):
        logging.basicConfig(level=config.logging_level)
        logger = logging.getLogger('SpeedTrap.LocalTools')
        logger.debug("Entering clean_local()")
        for filename in os.listdir(config.storage_path):
            if filename.endswith(config.database_filename):
                os.remove(config.database_path+filename)
            if filename.endswith(config.camera_file_extension):
                os.remove(config.database_path+filename)
        logger.debug("Leaving clean_local()")
