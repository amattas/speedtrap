class SpeedRecord:
    """
    The SpeedRecord class is used to pass around metadata around a speed event so it can be logged and uploaded
    to a cloud service. Logging is not used in this class because the Python logger creates a lock and prevents
    the class from being serialized successfully with pickle. Since these objects are passed between
    multiprocessing.Pipes() serialization is required.
    """

    def __init__(self, time, filename, speed):
        """
        This is the constructor used for class initialization

        Parameters
        ----------
        time : datetime
            This is the time the record occurred at
        filename : str
            This is the filename for the video stored
        speed : float
            This is the speed recorded

        Returns
        ------
        SpeedRecord:
            Returns a SpeedRecord instance initialized with the provided Configuration.
        -----
        """
        self._time = time
        self._filename = filename
        self._speed = speed

    def get_time(self):
        """
        Returns the time stored in the SpeedRecord instance

        Returns
        ------
        time:
            The time stored in the SpeedRecord instance
        -----
        """
        return self._time

    def get_filename(self):
        """
        Returns the filename stored in the SpeedRecord instance

        Returns
        ------
        str:
            The filename stored in the SpeedRecord instance
        -----
        """
        return self._filename

    def get_speed(self):
        """
        Returns the speed stored in the SpeedRecord instance

        Returns
        ------
        float:
            The speed stored in the SpeedRecord instance
        -----
        """
        return self._speed
