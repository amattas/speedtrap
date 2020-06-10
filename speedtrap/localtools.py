import os
import logging


class LocalTools:
    """
    This class is a helper class used to provide simple helper methods on the local system.
    """

    def __init__(self, config):
        """
        This is the constructor used for class initialization

        Parameters
        ----------
        config : Configuration
            This is a populated instances of the Configuration class with all of the settings loaded fom the specified
            configuration file

        Returns
        ------
        LocalTools:
            Returns a LocalTools instance initialized with the provided Configuration.
        -----
        """
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.LocalTools')
        self.logger.debug("Creating LocalTools() instance")

    @staticmethod
    def clean_local(config):
        """
        This method is used to clean up local files on the local filesystem. It uses a instance of the
        Configuration class to determine which files need to be removed.

        Parameters
        ----------
        config : Configuration
            This is a populated instances of the Configuration class with all of the settings loaded fom the specified
            configuration file
        """
        logging.basicConfig(level=config.logging_level)
        logger = logging.getLogger('SpeedTrap.LocalTools')
        logger.debug("Entering (static) clean_local()")
        for filename in os.listdir(config.storage_path):
            if filename.endswith(config.database_filename):
                os.remove(config.database_path+filename)
                logger.debug("Successfully removed %s", filename)
            if filename.endswith(config.camera_file_extension):
                os.remove(config.database_path+filename)
                logger.debug("Successfully removed %s", filename)
        logger.debug("Leaving clean_local()")
