import logging
import csv
import time
from speedtrap.cloudstorage import CloudStorage
from speedtrap.speedrecord import SpeedRecord

from speedtrap.odbcdatabase import ODBCDatabase

# ToDo: Document Class
class Scribe:
    """
    The DataRecorder class is designed to take a SpeedRecord and create a log entry either locally or on cloud
    storage
    """

    def __init__(self, config):
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.DataRecorder')
        self.logger.debug("Creating DataRecorder() instance")
        self._odbc_database = ODBCDatabase(config)

    def capture(self, data_child):
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
        self.logger.debug("Entering _record_storage()")
        record = [(speed, time.strftime('%Y-%m-%d %H:%M:%S', recorded_time), filename)]
        csv_filename = self._config.database_path + self._config.database_filename
        csv_file = open(csv_filename,'a')
        csv_writer = csv.writer(csv_file, dialect='excel')
        csv_writer.writerows(record)
        csv_file.close()
        self.logger.debug("Entering _record_storage()")
