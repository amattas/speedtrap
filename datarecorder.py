import logging;
import csv;
import time;


class DataRecorder:

    def __init__(self, config):
        self.logger = logging.getLogger('SpeedTrap')
        self.logger.debug("Creating DataRecorder() instance")
        self._load_config(config)

    def _load_config(self, config):
        self.logger.debug("Entering _load_config()")
        self._database_type = config['DATABASE']['DatabaseType']
        if self._database_type == 'LocalOnly':
            self._database_path = config['DATABASE']['DatabasePath']
            self._database_filename = config['DATABASE']['DatabaseFilename']
        self.logger.debug("Leaving _load_config()")

    def record(self, speed, time, file_uri):
        self.logger.debug("Entering record()")
        if self._database_type == 'LocalOnly':
            self._record_storage(speed, time, file_uri)
        self.logger.debug("Leaving record()")

    def _record_storage(self, speed, recorded_time, file_uri):
        self.logger.debug("Entering _record_storage()")
        record = [(speed, time.strftime('%Y-%m-%d %H:%M:%S', recorded_time), file_uri)]
        csv_filename = self._database_path + self._database_filename
        csv_file = open(csv_filename,'a')
        csv_writer = csv.writer(csv_file, dialect='excel')
        csv_writer.writerows(record)
        csv_file.close()
        self.logger.debug("Entering _record_storage()")
