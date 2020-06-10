import logging
import multiprocessing
import pyodbc
import time


class ODBCDatabase:
    """
    This class is a helper class used tp save a SpeedRecord into an ODBC database connection. It uses the data from
    the Configuration object specified to determine the connection information for the database.
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
        OBCDatabase:
            Returns a ODBCDatabase instance initialized with the provided Configuration.
        -----
        """
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.ODBCDatabase')
        self.logger.debug("Creating ODBCDatabase() instance")
        self._cloud_storage_thread = None

    def database_record(self, speed, recorded_time, file_uri=None):
        """
        This method is called to write a SpeedRecord to the database. It uses multiprocessing.Process to create
        a new Process to ensure we aren't blocking on the database write. The database connection information is derived
        from the Configuration instance provided when calling the constructor

        Parameters
        ----------
        speed : str
            This is the speed registered during the event that you want stored to store to the databse.
        recorded_time: time
            This is the time of the event you want to record to the database
        file_uri: str
            This is the uri of the file that you want to store in the database

        -----
        """
        self.logger.debug("Entering database_record()")
        if not self._config.enable_azure:
            self.logger.info("Unable to save record to cloud, azure is not enabled")
            return
        elif self._config.enable_azure:
            self.logger.debug("Starting thread to record database record")
            self._cloud_storage_thread = multiprocessing.Process(target=self._database_record, args=(speed, recorded_time, file_uri))
            self._cloud_storage_thread.start()
        self.logger.debug("Leaving database_record()")

    def _database_record(self, speed, recorded_time, file_uri=None):
        """
        This private method is instantiates the database connection using the Configuration object provided when the
        class was instantiated. It uses parameterized ODBC queries to write the data.

        Parameters
        ----------
        speed : str
            This is the speed registered during the event that you want stored to store to the databse.
        recorded_time: time
            This is the time of the event you want to record to the database
        file_uri: str
            This is the uri of the file that you want to store in the database

        -----
        """
        self.logger.debug("Entering _database_record()")
        database_connection = pyodbc.connect(self._config.database_connection_string)
        database_cursor = database_connection.cursor()
        database_query = ("INSERT INTO dbo.speedtrap (DateRecorded, SpeedRecorded, VideoUri) VALUES (?, ?, ?)")
        database_parameters = (time.strftime('%Y-%m-%d %H:%M:%S', recorded_time), speed, file_uri)
        database_cursor.execute(database_query, database_parameters)
        database_cursor.commit()
        self.logger.debug("Database record written successfully")
        database_cursor.close()
        self.logger.debug("Leaving _database_record()")
