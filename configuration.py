import configparser


class Configuration:

    def __init__(self, config_filename):
        self._config_parser = configparser.ConfigParser()
        self._config_parser.read('config.ini')

        # Load Default Configuration Section
        self.log_threshold = int(self._config_parser['DEFAULT']['LogThreshold'])
        self.record_threshold = int(self._config_parser['DEFAULT']['RecordThreshold'])
        self.clear_local_on_start = self._config_parser.getboolean('DEFAULT','ClearLocalOnStart')
        self.enable_azure = self._config_parser.getboolean('DEFAULT','EnableAzure')

        # Load Database Configuration Section
        self.enable_local_database = self._config_parser.getboolean('DATABASE','EnableLocalDatabase')
        self.database_path = self._config_parser['DATABASE']['DatabasePath']
        self.database_filename = self._config_parser['DATABASE']['DatabaseFilename']
        if self.enable_azure:
            self.azure_database_host = self._config_parser['DATABASE']['DatabaseAzureDatabaseHost']
            self.azure_database_user = self._config_parser['DATABASE']['DatabaseAzureDatabaseUser']
            self.azure_database_password = self._config_parser['DATABASE']['DatabaseAzureDatabasePassword']

        # Load Storage Configuration Section
        self.storage_path = self._config_parser['STORAGE']['StoragePath']
        if self.enable_azure:
            self.azure_storage_account = self._config_parser['STORAGE']['StorageAzureStorageAccountName']
            self.azure_storage_container = self._config_parser['STORAGE']['StorageAzureStorageContainer']
            self.azure_storage_key = self._config_parser['STORAGE']['StorageAzureStorageKey']
            self.storage_delete_on_upload = self._config_parser.getboolean('STORAGE','StorageDeleteOnUpload')

        self.camera_xresolution = int(self._config_parser['CAMERA']['XResolution'])
        self.camera_yresolution = int(self._config_parser['CAMERA']['YResolution'])
        self.camera_framerate = int(self._config_parser['CAMERA']['FrameRate'])
        self.camera_fourcc_codec = self._config_parser['CAMERA']['FourCCVideoCodec']
        self.camera_file_extension = self._config_parser['CAMERA']['FileExtension']
