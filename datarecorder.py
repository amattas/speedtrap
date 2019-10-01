import logging;
import csv;
import time;

from odbcdatabase import ODBCDatabase

class DataRecorder:

    def __init__(self, config):
        self.logger = logging.getLogger('SpeedTrap')
        self.logger.debug("Creating DataRecorder() instance")
        self._config = config
        self._odbc_database = ODBCDatabase(config)

    def record(self, speed, recorded_time, file_uri=None):
        self.logger.debug("Entering record()")
        if self._config.enable_local_database:
            self._record_storage(speed, recorded_time, file_uri)
        if self._config.enable_odbc:
            self._odbc_database.database_record(speed, recorded_time, file_uri)
        self.logger.debug("Leaving record()")

    def _record_storage(self, speed, recorded_time, file_uri=None):
        self.logger.debug("Entering _record_storage()")
        record = [(speed, time.strftime('%Y-%m-%d %H:%M:%S', recorded_time), file_uri)]
        csv_filename = self._config.database_path + self._config.database_filename
        csv_file = open(csv_filename,'a')
        csv_writer = csv.writer(csv_file, dialect='excel')
        csv_writer.writerows(record)
        csv_file.close()
        self.logger.debug("Entering _record_storage()")
