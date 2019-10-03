import serial
import logging
import time

class Radar:

    def __init__(self, config):
        self._config = config
        logging.basicConfig(level=self._config.logging_level)
        self.logger = logging.getLogger('SpeedTrap.Radar')
        self.logger.debug("Creating Radar() instance")
        self._config = config
        self._serial_connection = None
        #Handle busy serial port
        for _retry in range(5):
            try:
                serial.Serial(
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
                else:
                    self.logger.debug("Serial port busy, connection attempt #%s, failed", _retry)
                    raise
                time.sleep(3)
                pass
        self._configure_serial_device()

    def _configure_serial_device(self):
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

    # sendSerialCommand: function for sending commands to the OPS-241A module
    def send_serial_command(self, command):
        self.logger.debug("Entering send_serial_command()")
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
            if (data_rx_length != 0):
                data_rx_str = str(data_rx_bytes)
                self.logger.debug("Radar buffer contained: %s", data_rx_str)
                if data_rx_str.find(ser_message_start):
                    ser_write_verify = True
        self.logger.debug("Leaving send_serial_command()")

    def read_serial_buffer(self):
        Ops241_rx_bytes = self._serial_connection.readline()
        Ops241_rx_string = Ops241_rx_bytes.decode()
        self.logger.debug("Radar buffer contained: %s", Ops241_rx_string)
        return str(Ops241_rx_string)

