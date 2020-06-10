import logging
import csv
import time
from speedtrap.cloudstorage import CloudStorage
from speedtrap.speedrecord import SpeedRecord

from speedtrap.odbcdatabase import ODBCDatabase

# ToDo: Document Class
class Scribe:
    """
    The Scribe class is designed to take a SpeedRecord and and handle down stream "data" management, including writing
    the record out locally to CSV or to a database, and managing any necessary file uploads.
    """

    def __init__(self, config):
        """
        This is the constructor used for class initialization

        Parameters
        ----------
        config : Configuration
            This is a populated instance of the Configuration class with all of the settings loaded fom the specified
            configuration file

        Returns
        ------
        Scribe:
            Returns a Scribe instance initialized with the provided Configuration.
        -----
        """
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.DataRecorder')
        self.logger.debug("Creating DataRecorder() instance")
        self._odbc_database = ODBCDatabase(config)

    def capture(self, data_child):
        """
        Listens for messages arriving on a multiprocessing.Pipe() and takes the necessary actions. This method is
        intended to be called as its own multiprocessing.Process()

        Parameters
        ----------
        data_child : Pipe()
            This is one half of a bidirectional multiprocessing.Pipe(). It's used to control the behavior of the
            method. Possible values include: -1 which will cause the process to clean-up and exit gracefully or it can
            also receive a SpeedRecord object instance. When receiving a SpeedRecord object is passes it on and calls
            the private _save_record method.
        """
        data_result = 0
        while True:
            if data_child.poll():
                data_result = data_child.recv()
                if type(data_result) is int:
                    if data_result == -1:
                        self.logger.debug("Received -1 termination message")
                        break
                elif type(data_result) is SpeedRecord:
                    self._save_record(data_result.get_speed(), data_result.get_time(), data_result.get_filename())

    def _save_record(self, speed, recorded_time, filename):
        """
        This private method processes the information contained in a SpeedRecord and dispatches it based on in the
        Configuration instance provided with the calss was instantiated.

        Parameters
        ----------
        speed : str
            This is the speed of the event provided in the SpeedRecord
        recorded_time: time
            This is the time of the event provided in the SpeedRecord
        filename: str
            This is the name of the file provided in the SpeedRecord
        """
        self.logger.debug("Entering record()")
        if self._config.enable_local_database:
            self._record_storage(speed, recorded_time, filename)
        if self._config.enable_azure:
            cloud_storage = CloudStorage(self._config)
            cloud_storage.store_cloud_image(filename)
            if self._config.enable_odbc:
                self._odbc_database.database_record(speed, recorded_time, self._config.azure_storage_uri_prefix + filename)
        elif self._config.enable_odbc:
            self._odbc_database.database_record(speed, recorded_time, filename)

        self.logger.debug("Leaving record()")

    def _record_storage(self, speed, recorded_time, filename):
        """
        This private method store a copy of the SpeedRecrod as a CSV in the local filesystem storage

        Parameters
        ----------
        speed : str
            This is the speed of the event to store to local storage
        recorded_time: time
            This is the time of the event to store to local st orage
        filename: str
            This is the name of the file to store to local storage
        """
        self.logger.debug("Entering _record_storage()")
        record = [(speed, time.strftime('%Y-%m-%d %H:%M:%S', recorded_time), filename)]
        csv_filename = self._config.database_path + self._config.database_filename
        csv_file = open(csv_filename,'a')
        csv_writer = csv.writer(csv_file, dialect='excel')
        csv_writer.writerows(record)
        csv_file.close()
        self.logger.debug("Entering _record_storage()")
