import logging
import threading
import os
from azure.storage.blob import BlockBlobService


class CloudDatabase:

    def __init__(self, config):
        self.logger = logging.getLogger('SpeedTrap')
        self.logger.debug("Creating CloudDatabase() instance")
        self._config = config
        self._cloud_storage_thread = None

    def cloud_record(self, speed, recorded_time, file_uri=None):
        self.logger.debug("Entering cloud_record()")
        if not self._config.enable_azure:
            self.logger.info("Unable to save record to cloud, azure is not enabled")
            return
        elif self._config.enable_azure:
            self.logger.debug("Storing record to azure database")
            self._cloud_storage_thread = threading.Thread(target=self._azure_record, args=[speed, recorded_time, file_uri])
            self._cloud_storage_thread.start()
        self.logger.debug("Leaving cloud_record()")

    def _azure_record(self, speed, recoreded_time, file_uri=None):
        self.logger.debug("Entering _azure_record()")
        self.logger.debug("Leaving _azure_record()")