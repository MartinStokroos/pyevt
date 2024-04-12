# -*- coding:utf-8 -*-

import hid
from types import *
import time


class EvtExchanger:
    """This class is to communicate with EVTx devices."""

    selectedDevice = None
    listOfDevices = []
    Path = []

    def __init__(self):
        try:
            self.Attached()
        except Exception as e:
            raise(e)
            # raise Exception('EventExchanger (LibUSB) Initialisation Error')

    def Attached(self, matchingkey="EventExchanger"):
        """
        Attach EVT hardware.

        Parameters:
            matchingkey (string): attaches the available EVT2 device containing
            the string "EventExchanger".
        """
        self.selectedDevice = hid.device()
        self.listOfDevices = []
        self.Path = None
        self.selectedDevice.close()
        for d in hid.enumerate():
            longname = d["product_string"] + " SN## " + d["serial_number"]
            if matchingkey in longname:
                if self.listOfDevices == []:
                    self.Path = d['path']
                    self.selectedDevice.open_path(self.Path)
                    self.selectedDevice.set_nonblocking(True)
                    self.listOfDevices.append(longname)
        return (self.listOfDevices)

    def Select(self, deviceName):
        """
        Select device.

        Parameters:
            deviceName (string): select the device with string
            containing "device name".
        """
        self.Attached(deviceName)
        if type(self.Path) == bytes:
            self.selectedDevice.close()
            self.selectedDevice.open_path(self.Path)
            self.selectedDevice.set_nonblocking(True)
        else:
            self.selectedDevice = None
        return self.selectedDevice

    def WaitForDigEvents(self, AllowedEventLines, TimeoutMSecs):
        """
        Wait for incoming digital events based on polling.

        Parameters:
            AllowedEventLines: bit mask [0-255] to select the
            digital input lines.
            TimeoutMSecs: timeout period in ms
        Returns:
        """
        # flush the buffer!
        while (self.selectedDevice.read(1) != []):
            continue

        TimeoutSecs = TimeoutMSecs / 1000
        startTime = time.time()

        while 1:
            elapsedSecs = (time.time()-startTime)
            lastButton = self.selectedDevice.read(1)
            if (lastButton != []):
                if (lastButton[0] & AllowedEventLines > 0):
                    break
            # break for timeout:
            if (TimeoutMSecs != -1):
                if (elapsedSecs >= (TimeoutSecs)):
                    lastButton = [-1]
                    elapsedSecs = TimeoutSecs
                    break
        return lastButton[0], round(1000.0 * elapsedSecs)

    def GetAxis(self, ):
        """
        GetAxis data.

        Parameters: -

        Returns:
        """
        while (self.selectedDevice.read(1) != []):
            pass
        time.sleep(.01)
        valueList = self.selectedDevice.read(3)
        if (valueList == []):
            return self.__AxisValue
        self.__AxisValue = valueList[1] + (256*valueList[2])
        return self.__AxisValue

    # Functions that only require a single USB command to be sent to the device.
    def SetLines(self, outValue):
        """
        Set output lines.

        Parameters:
            outValue: bit pattern [0-255] to set the digital output lines.
        """
        self.selectedDevice.write(
            [0, self.__SETOUTPUTLINES, outValue, 0, 0, 0, 0, 0, 0, 0, 0])

    def PulseLines(self, outValue, durationInMillisecs):
        """
        Pulse output lines.

        Parameters:
            outValue: bit pattern [0-255] to pulse the digital output lines.
            durationInMillisecs: sets the duration of the pulse.
        """
        self.selectedDevice.write(
            [0, self.__PULSEOUTPUTLINES, outValue, durationInMillisecs & 255,
             durationInMillisecs >> 8, 0, 0, 0, 0, 0, 0])

    def SetAnalogEventStepSize(self, numberOfSamplesPerStep):
        """
        Set analog event step size.

        Parameters:
            numberOfSamplesPerStep: set the number of samples per step.
        """
        self.selectedDevice.write(
            [0, self.__SETANALOGEVENTSTEPSIZE, numberOfSamplesPerStep,
             0, 0, 0, 0, 0, 0, 0, 0])

    def RENC_SetUp(self, encRange, minimumValue, position,
                   inputChange, pulseInputDivider):
        """
        Rotary Encoder setup.

        Parameters:
            encRange:
            minumumValue:
            position:
            inputChange:
            pulseInputDivider:
        """
        self.__AxisValue = position
        self.selectedDevice.write(
            [0, self.__SETUPROTARYCONTROLLER, encRange & 255, encRange >> 8,
             minimumValue & 255, minimumValue >> 8, position & 255,
             position >> 8, inputChange, pulseInputDivider, 0])

    def RENC_Setposition(self, position):
        """Rotary Encoder set position.

            Parameters:
                position: Set the current position.
        """
        self.__AxisValue = position
        self.selectedDevice.write(
            [0, self.__SETROTARYCONTROLLERposition, position & 255,
             position >> 8, 0, 0, 0, 0, 0, 0, 0])

    def SetLedColor(self, redValue, greenValue, blueValue, ledNumber, mode):
        """Set LED color.

        Parameters:
            redValue:
            greenValue:
            blueValue:
            ledNumber:
            mode:
        """
        self.selectedDevice.write(
            [0, self.__SETWS2811RGBLEDCOLOR, redValue, greenValue,
             blueValue, ledNumber, mode, 0, 0, 0, 0])

    def SendColors(self, numberOfLeds, mode):
        """Set LED color.

        Parameters:
            redValue:
            greenValue:
            blueValue:
            ledNumber:
            mode:
        """
        self.selectedDevice.write(
            [0, self.__SENDLEDCOLORS, numberOfLeds, mode,
             0, 0, 0, 0, 0, 0, 0])

    def Reset(self):
        """
        Reset EVT device. WARNING! Will disconnect the device from USB.

        """
        self.selectedDevice.write(
            [0, self.__RESET, 0, 0, 0, 0, 0, 0, 0, 0, 0])

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
