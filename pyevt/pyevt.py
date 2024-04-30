# -*- coding:utf-8 -*-

import hid
# import sys
from types import *
import time


class EVTDeviceHandler:
    """This class is to communicate with EVTx devices."""

    def __init__(self, matching_key):
        self.device = None
        self.matching_key = matching_key

    def attach_device(self):
        """
        Attach EVT hardware.

        Parameters:
            matchingkey (string): attaches the available EVT2 device containing
            the string "EventExchanger".
        """
        # Attempt to list all connected HID devices
        all_devices = hid.enumerate()

        # Filter out the device by partial product name match
        for device_info in all_devices:
            if self.matching_key.lower() in device_info['product_string'].lower():
                try:
                    # Open the device
                    self.device = hid.device()
                    self.device.open_path(device_info['path'])
                    print(f"Device partially matched '{device_info['product_string']}' \
                          and attached successfully as '{self.matching_key}'.")
                    return True
                except IOError as e:
                    print(f"Failed to attach device: {e}")
                    return False

        print("Device not found that matches the partial name.")
        return False

    def select_device(self, device_name):
        """
        select device.

        Parameters:
            device_name (string): select the device with string
            containing "device name".
        """
        self.attach_device(device_name)
        if type(self.device) == bytes:
            self.device.close()
            self.device.open_path(self.device)
            self.device.set_nonblocking(True)
        else:
            self.device = None
        return self.device
    
    def close_device(self):
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
        # flush the buffer!
        while (self.device.read(1) != []):
            continue
        if isinstance(timeout_ms, int):
            TimeoutSecs = timeout_ms / 1000
        startTime = time.time()
        while 1:
            elapsedSecs = (time.time()-startTime)
            lastButton = self.device.read(1)
            if (lastButton != []):
                if (lastButton[0] & allowed_event_lines > 0):
                    break
            # break for timeout:
            if isinstance(timeout_ms, int):
                if (elapsedSecs >= (TimeoutSecs)):
                    lastButton = [-1]
                    elapsedSecs = TimeoutSecs
                    break
        return lastButton[0], round(1000.0 * elapsedSecs)

    def get_axis(self):
        """
        GetAxis data.

        Parameters: -

        Returns:
        """
        while (self.device.read(1) != []):
            pass
        time.sleep(.01)
        valueList = self.device.read(3)
        if (valueList == []):
            return self.__AxisValue
        self.__AxisValue = valueList[1] + (256*valueList[2])
        return self.__AxisValue

    # Single command device functions:
    def write_lines(self, output_value):
        """
        Set output lines.

        Parameters:
            output_value: bit pattern [0-255] to set the digital output lines.
        """
        if self.device is None:
            print("No device attached.")
            return False
        
        try:
            self.device.write(
                [0, self.__SETOUTPUTLINES, output_value, 0, 0, 0, 0, 0, 0, 0, 0])
            return True
        except IOError as e:
            print(f"Error in sending data: {e}")
            return False

    def pulse_lines(self, output_value, duration_ms):
        """
        Pulse output lines.

        Parameters:
            output_value: bit pattern [0-255] to pulse the 
            digital output lines.
            duration_ms: sets the duration of the pulse.
        """
        self.device.write(
            [0, self.__PULSEOUTPUTLINES, output_value, duration_ms & 255,
             duration_ms >> 8, 0, 0, 0, 0, 0, 0])

    def set_analog_event_step_size(self, no_samples_per_step):
        """
        Set analog event step size.

        Parameters:
            no_samples_per_step: set the number of samples per step.
        """
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
        self.device.write(
            [0, self.__SENDLEDCOLORS, number_of_leds, mode,
             0, 0, 0, 0, 0, 0, 0])

    def reset_device(self):
        """
        Reset EVT device. WARNING! Will disconnect the device from USB.

        """
        self.device.write(
            [0, self.__RESET, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        if self.device:
            self.device.close()

    __AxisValue = 0

    # CONSTANTS:
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
