import logging
import threading
import os
from azure.storage.blob import BlockBlobService


class CloudStorage:

    def __init__(self, config):
        self.logger = logging.getLogger('SpeedTrap')
        self.logger.debug("Creating CloudStorage() instance")
        self._config = config
        self._cloud_storage_thread = None

    def store_cloud_image(self, filename):
        self.logger.debug("Entering store_cloud_image()")
        if not self._config.enable_azure:
            self.logger.info("Unable to save %s to cloud, configured for local storage only", filename)
            return
        elif self._config.enable_azure:
            self.logger.debug("Starting thread to store %s to AzureBlobStorage", filename)
            self._cloud_storage_thread = threading.Thread(target=self._store_azure_blob, args=[filename])
            self._cloud_storage_thread.start()
        self.logger.debug("Leaving store_cloud_image()")

    def _store_azure_blob(self, filename):
        self.logger.debug("Entering _store_azure_blob()")
        self.logger.debug("Creating BlobServiceClient")
        storage_service = BlockBlobService(account_name=self._config.azure_storage_account,
                                           account_key=self._config.azure_storage_key)
        self.logger.debug("Writing File %s", filename)
        # storage_container =  storage_service.acquire_container_lease(self._azure_storage_container)
        self.logger.debug("Getting BlobClient %s", filename)
        storage_service.create_blob_from_path(container_name=self._config.azure_storage_container,
                                              blob_name=filename,
                                              file_path=self._config.storage_path + filename)
        if self._config.storage_delete_on_upload:
            self.logger.debug("Deleting file %s", filename)
            os.remove(self._config.storage_path + filename)
        self.logger.debug("Leaving _store_azure_blob()")