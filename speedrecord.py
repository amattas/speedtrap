class SpeedRecord:
    """
    The SpeedRecord class is used to pass around metadata around a speed event so it can be logged and uploaded
    to a cloud service
    """

    def __init__(self, time, filename, speed):
        self._time = time
        self._filename = filename
        self._speed = speed

    def get_time(self):
        return self._time

    def set_time(self, time):
        self._time = time

    def get_filename(self):
        return self._filename

    def set_filename(self, filename):
        self._filename = filename

    def get_speed(self):
        return self._speed

    def set_speed(self, speed):
        self._speed = speed

