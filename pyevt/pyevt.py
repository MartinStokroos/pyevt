# -*- coding:utf-8 -*-

import hid
# import sys
from types import *
import time


class EventExchanger:
    """This class is to communicate with EVTx devices."""

    def __init__(self):
        self.device = None

    def attach(self, matching_key):
        """
        Attach EVT-device

        Parameters:
            matchingkey (string): attaches the available EVT2 device containing
            the string "EventExchanger".
        """
        # Attempt to list all connected HID devices
        all_devices = hid.enumerate()
        list_of_devices = []

        # Filter out the device by partial product name match
        for d in all_devices:
            if matching_key.lower() in d['product_string'].lower():
                try:
                    # Open the device
                    self.device = hid.device()
                    self.device.open_path(d['path'])
                    print(f"Device partially matched '{d['product_string']}' \
                          and attached successfully as '{matching_key}'.")
                    self.device.set_nonblocking(True)
                    product_string = d["product_string"]
                    device_alias = product_string[15:24] + " S/N #" + d["serial_number"]
                    list_of_devices.append(device_alias)
                    return list_of_devices
                except IOError as e:
                    print(f"Failed to attach device: {e}")
                    return False
        print("Device not found that matches the partial name.")
        return False

    def close(self):
        """
        Close EVT device.

        Parameters:
            -
        """
        if self.device:
            self.device.close()

    def wait_for_event(self, allowed_event_lines, timeout_ms):
        """
        Wait for incoming digital events based on polling.

        Parameters:
            allowed_event_lines: bit mask [0-255] to select the
            digital input lines.
            timeout_ms: timeout period in ms. Set to None for infinite.
        Returns:
        """
        if self.device is None:
            print("No device attached.")
            return None

        if allowed_event_lines is not None:
            bit_mask = int(allowed_event_lines)

        t_start = time.time()
        # flush the buffer!
        while (self.device.read(self.__RXBUFSIZE) != []):
            continue
        # Blocking loop. read() itself is non-blocking.
        while True:
            last_event = self.device.read(self.__RXBUFSIZE)
            t_elapsed = (time.time() - t_start) * 1000 # convert seconds to milliseconds
            if (last_event != []):
                if ((last_event[0] & bit_mask) > 0):
                    break
            # break for timeout:
            if timeout_ms is not None:
                if (t_elapsed >= int(timeout_ms)):
                    last_event = [-1]
                    # t_elapsted = timeout
                    break
        return last_event[0], round(t_elapsed)

    def get_axis(self):
        """
        GetAxis data.

        Parameters: -

        Returns:
        """
        if self.device is None:
            print("No device attached.")
            return None

        while (self.device.read(1) != []):
            pass
        time.sleep(.01)
        valueList = self.device.read(3)
        if (valueList == []):
            return self.__AxisValue
        self.__AxisValue = valueList[1] + (256*valueList[2])
        return self.__AxisValue

    # Single command device functions:
    def write_lines(self, value):
        """
        Set output lines.

        Parameters:
            value: bit pattern [0-255] to set the digital output lines.
        """
        if self.device is None:
            print("No device attached.")
            return False
        
        try:
            self.device.write(
                [0, self.__SETOUTPUTLINES, value, 0, 0, 0, 0, 0, 0, 0, 0])
            return True
        except IOError as e:
            print(f"Error in sending data: {e}")
            return False

    def pulse_lines(self, value, duration_ms):
        """
        Pulse output lines.

        Parameters:
            value: bit pattern [0-255] to pulse the 
            digital output lines.
            duration_ms: sets the duration of the pulse.
        """
        if self.device is None:
            print("No device attached.")
            return None
        
        self.device.write(
            [0, self.__PULSEOUTPUTLINES, value, duration_ms & 255,
             duration_ms >> 8, 0, 0, 0, 0, 0, 0])

    def set_analog_event_step_size(self, no_samples_per_step):
        """
        Set analog event step size.

        Parameters:
            no_samples_per_step: set the number of samples per step.
        """
        if self.device is None:
            print("No device attached.")
            return None
        
        self.device.write(
            [0, self.__SETANALOGEVENTSTEPSIZE, no_samples_per_step,
             0, 0, 0, 0, 0, 0, 0, 0])

    def renc_init(self, encoder_range, min_value, position,
                   input_change, pulse_input_divider):
        """
        Rotary Encoder setup.

        Parameters:
            encoder_range:
            minumumValue:
            position:
            input_change:
            pulse_input_divider:
        """
        if self.device is None:
            print("No device attached.")
            return None

        self.__AxisValue = position
        self.device.write(
            [0, self.__SETUPROTARYCONTROLLER, encoder_range & 255,
             encoder_range >> 8, min_value & 255, min_value >> 8,
             position & 255, position >> 8,
             input_change, pulse_input_divider, 0])

    def renc_set_pos(self, position):
        """Rotary Encoder set position.

            Parameters:
                position: Set the current position.
        """
        if self.device is None:
            print("No device attached.")
            return None

        self.__AxisValue = position
        self.device.write(
            [0, self.__SETROTARYCONTROLLERposition, position & 255,
             position >> 8, 0, 0, 0, 0, 0, 0, 0])

    def set_led_rgb(self, red_value, green_value, blue_value,
                    led_number, mode):
        """Set LED color.

        Parameters:
            red_value:
            green_value:
            blue_value:
            led_number:
            mode:
        """
        if self.device is None:
            print("No device attached.")
            return None

        self.device.write(
            [0, self.__SETWS2811RGBLEDCOLOR, red_value, green_value,
             blue_value, led_number, mode, 0, 0, 0, 0])

    def send_led_rgb(self, number_of_leds, mode):
        """Set LED color.

        Parameters:
            red_value:
            green_value:
            blue_value:
            led_number:
            mode:
        """
        if self.device is None:
            print("No device attached.")
            return None

        self.device.write(
            [0, self.__SENDLEDCOLORS, number_of_leds, mode,
             0, 0, 0, 0, 0, 0, 0])

    def reset_device(self):
        """
        Reset EVT device. WARNING! Will disconnect the device from USB.

        """
        if self.device is None:
            print("No device attached.")
            return None

        self.device.write(
            [0, self.__RESET, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        if self.device:
            self.device.close()


    __AxisValue = 0

    # CONSTANTS:
    __RXBUFSIZE = 1 # Receive buffer size=1

    __CLEAROUTPUTPORT = 0  # 0x00
    __SETOUTPUTPORT = 1  # 0x01
    __SETOUTPUTLINES = 2  # 0x02
    __SETOUTPUTLINE = 3  # 0x03
    __PULSEOUTPUTLINES = 4  # 0x04
    __PULSEOUTPUTLINE = 5  # 0x05

    __SENDLASTOUTPUTBYTE = 10  # 0x0A

    __CONVEYEVENT2OUTPUT = 20  # 0x14
    __CONVEYEVENT2OUTPUTEX = 21  # 0x15
    __CANCELCONVEYEVENT2OUTPUT = 22  # 0x16

    __CANCELEVENTREROUTES = 30  # 0x1E
    __REROUTEEVENTINPUT = 31  # 0x1F

    __SETUPROTARYCONTROLLER = 40  # 0x28
    __SETROTARYCONTROLLERposition = 41  # 0x29

    __CONFIGUREDEBOUNCE = 50  # 0x32

    __SETWS2811RGBLEDCOLOR = 60  # 0x3C
    __SENDLEDCOLORS = 61  # 0x3D

    __SWITCHALLLINESEVENTDETECTION = 100  # 0x64
    __SWITCHLINEEVENTDETECTION = 101  # 0x65

    __SETANALOGINPUTDETECTION = 102  # 0x66
    __REROUTEANALOGINPUT = 103  # 0X67
    __SETANALOGEVENTSTEPSIZE = 104  # 0X68

    __SWITCHDIAGNOSTICmode = 200  # 0xC8
    __SWITCHEVENTTEST = 201  # 0xC9

    __RESET = 255  # 0xFF

# -*- coding:utf-8 -*-
