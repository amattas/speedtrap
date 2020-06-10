import logging
import multiprocessing
import os
import azure.common
from azure.storage.blob import BlockBlobService


# Todo - comment class
class CloudStorage:
    """
    This class is a helper class used to upload an image file to a cloud storage account. Currently it only supports
    Azure, but others could be easily added if required by other users of the platform. The upload occures in its
    own process to ensure we aren't blocking any of the other activity happening.
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
        CloudStorage:
            Returns a CloudStorage instance initialized with the provided Configuration.
        -----
        """
        self._config = config
        logging.basicConfig(filename=self._config.logging_path, level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.CloudStorage')
        self.logger.debug("Creating CloudStorage() instance")
        self._cloud_storage_thread = None

    def store_cloud_image(self, filename):
        """
        Stores a filename to cloud storage. The configuration used when instantiating the class will be used to
        determine what type of cloud storage to store the file into, and whether to delete the local file or not.

        Parameters
        ----------
        filename : str
            Name of the file to be uploaded, it will automatically be appended with the file storage path form the
            configuration file.
        -----
        """
        self.logger.debug("Entering store_cloud_image()")
        if not self._config.enable_azure:
            self.logger.info("Unable to save %s to cloud, configured for local storage only", filename)
            return
        elif self._config.enable_azure:
            self.logger.debug("Starting thread to store %s to AzureBlobStorage", filename)
            self._cloud_storage_thread = multiprocessing.Process(target=self._store_azure_blob, args=(filename,))
            self._cloud_storage_thread.start()
        self.logger.debug("Leaving store_cloud_image()")

    def _store_azure_blob(self, filename):
        """
        Stores a filename to an Azure blob storage account. The configuration used when instantiating the class
        will be used to determine where the Azure storage account information, and whether or not to remove the file
        from local storage after a successful upload. It will attempt the upload 5 times before failing.

        Parameters
        ----------
        filename : str
            Name of the file to be uploaded, it will automatically be appended with the file storage path form the
            configuration file.
        -----
        """
        for retry_counter in range(5):
            try:
                self.logger.debug("Entering _store_azure_blob()")
                self.logger.debug("Creating BlobServiceClient")
                storage_service = BlockBlobService(account_name=self._config.azure_storage_account,
                                                   account_key=self._config.azure_storage_key)
                self.logger.debug("Attempting to save file %s to Azure", filename)
                # storage_container =  storage_service.acquire_container_lease(self._azure_storage_container)
                self.logger.debug("Getting BlobClient %s", filename)
                storage_service.create_blob_from_path(container_name=self._config.azure_storage_container,
                                                      blob_name=filename,
                                                      file_path=self._config.storage_path + filename)
                self.logger.info("File %s successfully saved to Azure", filename)
                if self._config.storage_delete_on_upload:
                    self.logger.debug("Deleting local file %s", filename)
                    os.remove(self._config.storage_path + filename)
                    self.logger.info("File %s successfully deleted from local filesystem", filename)
                    retry_counter = 6  # Stop retrying
                    break
            except azure.common.AzureException:
                self.logger.warning("Upload to Azure Storage failed on attempt %s", retry_counter+1)
                continue
        self.logger.debug("Leaving _store_azure_blob()")
