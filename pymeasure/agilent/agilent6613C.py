#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range

from pymeasure.adapters import VISAAdapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class Agilent6613C(Instrument):
    """ Represents the agilent 6613C outputMeter and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        agilent = Agilent6613C("GPIB::5")

        agilent.apply_current()                # Sets up to output current
        agilent.output_current_range = 10e-3   # Sets the output current range to 10 mA
        agilent.compliance_voltage = 10        # Sets the compliance voltage to 10 V
        agilent.output_current = 0             # Sets the output current to 0 mA
        agilent.enable_output()                # Enables the output output

        agilent.measure_voltage()              # Sets up to measure voltage

        print(agilent.voltage)                 # Prints the voltage in Volts

        agilent.shutdown()                     # Ramps the current to 0 mA and disables output

    """
    
    current_range = [0, 1.05]
    voltage_range = [0, 51]

    output_enabled = Instrument.control(
        "OUTPut?", "OUTPut %d",
        """ A boolean property that controls whether the output is enabled, takes
        values True or False. The convenience methods :meth:`~.agilent6613C.enable_output` and
        :meth:`~.agilent6613C.disable_output` can also be used.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    output_relay = Instrument.control(
        "OUTP:REL?", "OUTP:REL %d",
        """ A boolean property that controls whether the output relay is enabled, takes
        values True or False. When the output relay is enabled, the direction of the current
        can be changed with the output_relay_polarity control.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    output_relay_polarity = Instrument.control(
        "OUTP:REL:POL?", "OUTP:REL:POL %d",
        """ A boolean property that controls whether the output relay polarity is reversed, takes
        values True or False. When the output relay polarity is reversed, the direction of the current will
        be reversed, that is, positive current becomes negative current. """,
        values={True: "REV", False: "NORM"},
        map_values=True,
    )

    ###############
    # Current (A) #
    ###############

    output_current = Instrument.control(
        "CURR?", "CURR %g",
        """ A floating point property that controls the output current
        in Amps. """,
        validator=truncated_range,
        values=current_range
    )
    current_protection = Instrument.control(
        "CURR:PROT?", "CURR:PROT %g",
        """ A floating point property that controls the compliance current
        in Amps. """,
        validator=truncated_range,
        values=current_range
    )

    ###############
    # Voltage (V) #
    ###############

    output_voltage = Instrument.control(
        "VOLT?", "VOLT %g",
        """ A floating point property that controls the output current
        in Amps. """,
        validator=truncated_range,
        values=voltage_range
    )
    voltage_protection = Instrument.control(
        "VOLT:PROT?", "VOLT:PROT %g",
        """ A floating point property that controls the measurement voltage
        range in Volts, which can take values from -51 to 51 V. """,
        validator=truncated_range,
        values=voltage_range
    )
    
    # only the most simple functions are implemented
    voltage_dc = Instrument.measurement("MEAS:VOLT:DC? DEF,DEF", "DC voltage, in Volts")

    current_dc = Instrument.measurement("MEAS:CURR:DC? DEF,DEF", "DC current, in Amps")

    def __init__(self, adapter, name="HP/Agilent/Keysight 6613C Power Supply", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )

    def enable_output(self):
        """ Enables the output of current or voltage depending on the
        configuration of the instrument. """
        self.write("OUTP ON")

    def disable_output(self):
        """ Disables the output of current or voltage depending on the
        configuration of the instrument. """
        self.write("OUTP OFF")
        
    def output_current(self, curr):
            self.output_relay = True
        if -max(voltage_range) <= curr < min(voltage_range):
            self.output_relay_polarity = True
        elif min(voltage_range) <= curr <= max(voltage_range):
            self.output_relay_polarity = False
        else:
            raise ValueError('Value of {:g} is not in range [{:g},{:g}]'.format(
            curr, min(voltage_range), max(voltage_range)
            
    def output_voltage(self, curr):
        if min(voltage_range) <= volt <= max(voltage_range):
            