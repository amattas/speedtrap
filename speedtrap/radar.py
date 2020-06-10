import serial
import logging
import time

class Radar:
    """
    This is a helper class used to interface with the Omnipresense radar devices. To date it has only been used with
    the OPS243-A model, but many of the models are similar and this likely will work fine with other variations that
    have doppler capabilities.
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
        Radar:
            Returns a Radar instance initialized with the provided Configuration. A Serial connection is made to the
            device at instantiation time (this behavior may be changed in a future release)
        """
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.Radar')
        self.logger.debug("Creating Radar() instance")
        self._config = config
        self._serial_connection = None
        #Handle busy serial port
        for _retry in range(5):
            try:
                self._serial_connection = serial.Serial(
                    port=self._config.radar_device_path,
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1,
                    writeTimeout=2
                )
                break
            except:
                if _retry < 5:
                    self.logger.debug("Serial port busy, connection attempt #%s, retrying in 3 seconds", _retry)
                    time.sleep(3)
                    pass
                else:
                    self.logger.debug("Serial port busy, connection attempt #%s, failed", _retry)
                    raise


        self._configure_serial_device()

    def _configure_serial_device(self):
        """
        This private method sends all of the device setup parameters required to properly record. Each configuration
        parameter is a two character string. Details of the parameters can be found in document AN-010 from
        Omnipresense (at the time of writing the most recent location is here:
        https://omnipresense.com/wp-content/uploads/2019/10/AN-010-Q_API_Interface.pdf)
        """
        self._serial_connection.flushInput()
        self._serial_connection.flushOutput()
        self.send_serial_command(self._config.radar_speed_output_units)
        self.send_serial_command(self._config.radar_data_precision)
        self.send_serial_command(self._config.radar_sampling_rate)
        self.send_serial_command(self._config.radar_reported_minimum_speed)
        self.send_serial_command(self._config.radar_speed_reported_maximum)
        self.send_serial_command(self._config.radar_direction_control)
        self.send_serial_command(self._config.radar_speed_report)
        self.send_serial_command(self._config.radar_processing_light_activity)
        self.send_serial_command(self._config.radar_json_mode)
        self.send_serial_command(self._config.radar_processing_led_control)
        self.send_serial_command(self._config.radar_blank_data_reporting)
        self.send_serial_command(self._config.radar_transmit_power)

    def send_serial_command(self, command):
        """
        This method takes a text string and sends it over the serial connection to the radar device.

        Parameters
        ----------
        command : str
            This is command string being sent to the radar device.
        """
        self.logger.debug("Entering send_serial_command()")
        self.logger.debug("Flushing input buffer")
        self._serial_connection.flushInput()
        data_for_send_str = command
        data_for_send_bytes = str.encode(data_for_send_str)
        self.logger.debug("Sending command %s", command)
        self._serial_connection.write(data_for_send_bytes)
        # Initialize message verify checking
        ser_message_start = '{'
        ser_write_verify = False
        # Print out module response to command string
        while not ser_write_verify:
            data_rx_bytes = self._serial_connection.readline()
            data_rx_length = len(data_rx_bytes)
            if data_rx_length != 0:
                data_rx_str = str(data_rx_bytes)
                self.logger.debug("Radar buffer contained: %s", data_rx_str)
                if data_rx_str.find(ser_message_start):
                    ser_write_verify = True
        self.logger.debug("Leaving send_serial_command()")

    def read_serial_buffer(self):
        """
        This method reads the current serial buffer from the radar device.

        Returns
        -------
        String:
            This is the string of text on the serial buffer for the radar device
        """
        ops_rx_bytes = self._serial_connection.readline()
        ops_rx_string = ops_rx_bytes.decode()
        self.logger.debug("Radar buffer contained: %s", ops_rx_string)
        return str(ops_rx_string)

