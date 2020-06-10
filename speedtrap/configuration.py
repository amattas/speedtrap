import configparser
import logging


class Configuration:
    """
    This class is a helper class used to manage the configuration of the speedtrap. It reads an INI style configuration
    file and loads the values into this class to be consumed during execution. All of the work happens during the
    initialization of the class.
    """

    def __init__(self, config_filename):
        """
        This is the constructor used for class initialization

        Parameters
        ----------
        config_filename: str
            This is the full path for the configuration file used to populate the Configuration object.

        Returns
        -------
        Configuration:
            Returns a Configuration instance initialized with the values specified in config_filename
        -----
        """
        self._config_parser = configparser.ConfigParser()
        self._config_parser.read(config_filename)

        # Load Default Configuration Section
        self.record_threshold = int(self._config_parser['DEFAULT']['RecordThreshold'])
        self.clear_local_on_start = self._config_parser.getboolean('DEFAULT','ClearLocalOnStart')
        self.enable_azure = self._config_parser.getboolean('DEFAULT','EnableAzure')
        if self._config_parser['DEFAULT']['LogLevel'] == 'DEBUG':
            self.logging_level = logging.DEBUG
        elif self._config_parser['DEFAULT']['LogLevel'] == 'INFO':
            self.logging_level = logging.INFO
        else:
            self.logging_level = logging.WARN

        # Load Database Configuration Section
        self.enable_local_database = self._config_parser.getboolean('DATABASE','EnableLocalDatabase')
        self.database_path = self._config_parser['DATABASE']['DatabasePath']
        self.database_filename = self._config_parser['DATABASE']['DatabaseFilename']
        self.enable_odbc = self._config_parser.getboolean('DATABASE', 'EnableODBC')
        if self.enable_odbc:
            self.database_connection_string = self._config_parser['DATABASE']['DatabaseConnectionString']

        # ToDo: Make configurations true or false
        # Load Storage Configuration Section
        self.storage_path = self._config_parser['STORAGE']['StoragePath']
        if self.enable_azure:
            self.azure_storage_account = self._config_parser['STORAGE']['StorageAzureStorageAccountName']
            self.azure_storage_container = self._config_parser['STORAGE']['StorageAzureStorageContainer']
            self.azure_storage_key = self._config_parser['STORAGE']['StorageAzureStorageKey']
            self.azure_storage_uri_prefix = "https://{0!s}.blob.core.windows.net/{1!s}/".format(self.azure_storage_account, self.azure_storage_container)
            self.storage_delete_on_upload = self._config_parser.getboolean('STORAGE','StorageDeleteOnUpload')

        self.camera_xresolution = int(self._config_parser['CAMERA']['XResolution'])
        self.camera_yresolution = int(self._config_parser['CAMERA']['YResolution'])
        self.camera_framerate = int(self._config_parser['CAMERA']['FrameRate'])
        self.camera_fourcc_codec = self._config_parser['CAMERA']['FourCCVideoCodec']
        self.camera_file_extension = self._config_parser['CAMERA']['FileExtension']

        self.radar_device_path = self._config_parser['RADAR']['DevicePath']
        self.radar_speed_output_units = self._config_parser['RADAR']['SpeedOutputUnits']
        self.radar_data_precision = self._config_parser['RADAR']['DataPrecision']
        self.radar_sampling_rate = self._config_parser['RADAR']['SamplingRate']
        self.radar_reported_minimum_speed = "R>{!s}\r".format(self.record_threshold)
        self.radar_speed_reported_maximum = "R<0\r"
        self.radar_direction_control = self._config_parser['RADAR']['DirectionControl']
        self.radar_speed_report = self._config_parser['RADAR']['SpeedReport']
        self.radar_processing_light_activity = self._config_parser['RADAR']['ProcessingLightActivity']
        self.radar_json_mode = 'OJ'
        self.radar_processing_led_control = self._config_parser['RADAR']['LedControl']
        self.radar_blank_data_reporting = self._config_parser['RADAR']['BlankDataReporting']
        self.radar_transmit_power = self._config_parser['RADAR']['TransmitPower']
