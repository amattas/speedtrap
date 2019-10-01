import logging
import threading
import os
from azure.storage.blob import BlockBlobService
from enum import Enum

class CloudStorage:

    def __init__(self, config):
        self.logger = logging.getLogger('SpeedTrap')
        self.logger.debug("Creating CloudStorage() instance")
        self._load_config(config)

    def _load_config(self, config):
        self.logger.debug("Entering _load_config()")
        self._storage_path = config['STORAGE']['StoragePath']
        if int(config['STORAGE']['StorageDeleteOnUpload']) == 1:
            self._storage_delete_on_upload = True
        else:
            self._storage_delete_on_upload = False
        if config['STORAGE']['StorageType'] == 'LocalOnly':
            self.logger.debug("Storage client selected as LocalOnly")
            self._storage_type = StorageType.LOCAL_ONLY
        elif config['STORAGE']['StorageType'] == 'AzureBlobStorage':
            self.logger.debug("Storage client selected as AzureBlobStorage")
            self._storage_type = StorageType.AZURE_BLOB_STORAGE
            self._azure_storage_key = config['STORAGE']['StorageAzureStorageKey']
            self._azure_storage_account = config['STORAGE']['StorageAzureStorageAccountName']
            self._azure_storage_container = config['STORAGE']['StorageAzureStorageContainer']
        else:
            self.logger.error("An invalid storage option was provided")
            raise ValueError('An invalid storage option was provided')
        self.logger.debug("Leaving _load_config()")

    def store_cloud_image(self, filename):
        self.logger.debug("Entering store_cloud_image()")
        if self._storage_type == StorageType.LOCAL_ONLY:
            self.logger.info("Unable to save %s to cloud, configured for local storage only", filename)
            return
        elif self._storage_type == StorageType.AZURE_BLOB_STORAGE:
            self.logger.debug("Starting thread to store %s to AzureBlobStorage", filename)
            self._cloud_storage_thread = threading.Thread(target=self._store_azure_blob, args=[filename])
            self._cloud_storage_thread.start()
        self.logger.debug("Leaving store_cloud_image()")

    def _store_azure_blob(self, filename):
        self.logger.debug("Entering _store_azure_blob()")
        self.logger.debug("Creating BlobServiceClient")
        storage_service = BlockBlobService(account_name=self._azure_storage_account,
                                           account_key=self._azure_storage_key)
        self.logger.debug("Writing File %s", filename)
        # storage_container =  storage_service.acquire_container_lease(self._azure_storage_container)
        self.logger.debug("Getting BlobClient %s", filename)
        storage_service.create_blob_from_path(container_name=self._azure_storage_container,
                                                     blob_name=filename,
                                                     file_path=self._storage_path + filename)
        if self._storage_delete_on_upload:
            self.logger.debug("Deleting file %s", filename)
            os.remove(self._storage_path + filename)



class StorageType(Enum):
    LOCAL_ONLY = 0
    AZURE_BLOB_STORAGE = 1
