import pyvisa

class MeasurementDevice:
    def __init__(self, visa_address):
        """
        Initialize the MeasurementDevice object with the VISA address.

        Parameters:
        - visa_address (str): The VISA address of the measurement device.
        """
        self.visa_address = visa_address
        self.instrument = None

    def connect(self):
        """
        Connect to the measurement device using VISA.

        Raises:
        - Exception: If the connection to the device fails.
        """
        try:
            self.instrument = pyvisa.ResourceManager().open_resource(self.visa_address)
            print(f"Connected to the device at {self.visa_address}")
        except Exception as e:
            raise Exception(f"Failed to connect to the device: {str(e)}")

    def get_values(self):
        """
        Retrieve measurement values from the connected device.

        Returns:
        - str: Measurement values obtained from the device.

        Raises:
        - Exception: If there is an issue with communication or data retrieval.
        """
        try:
            values = self.instrument.query("READ?")  # Replace with the actual command for reading values
            return values
        except Exception as e:
            raise Exception(f"Failed to get values from the device: {str(e)}")

    def set_values(self, configuration):
        """
        Set configuration values on the connected device.

        Parameters:
        - configuration (str): Configuration settings to be set on the device.

        Raises:
        - Exception: If there is an issue with communication or setting values.
        """
        try:
            self.instrument.write(configuration)  # Replace with the actual command for setting values
            print(f"Configuration set: {configuration}")
        except Exception as e:
            raise Exception(f"Failed to set values on the device: {str(e)}")
'''
    def disconnect(self):
        ""
        Disconnect from the measurement device.

        Raises:
        - Exception: If there is an issue with disconnection.
        ""
        try:
            self.instrument.close()
            print("Disconnected from the device")
        except Exception as e:
            raise Exception(f"Failed to disconnect from the device: {str(e)}")
'''

if __name__ == "__main__":
    device = MeasurementDevice("GPIB0::19::INSTR")

    try:
        device.connect()

        # Set configuration values
        configuration_settings = "*RST"
        device.set_values(configuration_settings)

        # Retrieve and print measurement values
        values = device.get_values()
        print("Measured values:", values)

    except Exception as e:
        print(f"Error: {str(e)}")

    #finally:
        # Disconnect from the device in any case
        #device.disconnect()