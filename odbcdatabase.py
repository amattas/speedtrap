import logging
import threading
import pyodbc
import time


class ODBCDatabase:

    def __init__(self, config):
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.ODBCDatabase')
        self.logger.debug("Creating CloudDatabase() instance")
        self._cloud_storage_thread = None

    def database_record(self, speed, recorded_time, file_uri=None):
        self.logger.debug("Entering cloud_record()")
        if not self._config.enable_azure:
            self.logger.info("Unable to save record to cloud, azure is not enabled")
            return
        elif self._config.enable_azure:
            self.logger.debug("Storing record to azure database")
            self._cloud_storage_thread = threading.Thread(target=self._database_record, args=[speed, recorded_time, file_uri])
            self._cloud_storage_thread.start()
        self.logger.debug("Leaving cloud_record()")

    def _database_record(self, speed, recorded_time, file_uri=None):
        self.logger.debug("Entering _azure_record()")
        self.logger.debug("Leaving _azure_record()")
        database_connection = pyodbc.connect(self._config.database_connection_string)
        database_cursor = database_connection.cursor()
        database_query = ("INSERT INTO dbo.speedtrap (DateRecorded, SpeedRecorded, VideoUri) VALUES (?, ?, ?)")
        database_parameters = (time.strftime('%Y-%m-%d %H:%M:%S', recorded_time), speed, file_uri)
        #database_parameters = [(recorded_time, speed, file_uri)]
        database_cursor.execute(database_query, database_parameters)
        database_cursor.commit()
        database_cursor.close()
