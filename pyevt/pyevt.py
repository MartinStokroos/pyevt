#-*- coding:utf-8 -*-

'Python module for EVT2 devices.'

from libopensesame.oslogging import oslogger
import hid
import sys
from types import *
import os
import ctypes
import time


class EvtExchanger:
	"""This class is to communicate with EVT2 devices."""
	SelectedDevice = None
	ListOfDevices = []
	Path = []
	def __init__(self):
		try:
			self.Attached()
		except Exception as e:
			raise(e)
			#raise Exception('EventExchanger (LibUSB) Initialisation Error')

	def Attached(self, matchingkey = "EventExchanger"):
		"""Attach EVT hardware.
        
            Parameters:
                matchingkey (string): attaches the available EVT2 device containing the string "EventExchanger".
    	"""
		self.SelectedDevice = hid.device()
		self.ListOfDevices = []
		self.Path = None
		self.SelectedDevice.close()
		for d in hid.enumerate():
			longname = d["product_string"] + " SN## " + d["serial_number"]
			if matchingkey in longname:
				if self.ListOfDevices == []:
					self.Path = d['path']
					self.SelectedDevice.open_path(self.Path)
					self.SelectedDevice.set_nonblocking(True)
				self.ListOfDevices.append(longname)
		return (self.ListOfDevices)


	def Select(self, deviceName):
		"""Select device.
        
            Parameters:
                deviceName (string): select the device with string containing "device name".
		"""
		self.Attached(deviceName)
		if type(self.Path) == bytes:
			self.SelectedDevice.close()
			self.SelectedDevice.open_path(self.Path)
			self.SelectedDevice.set_nonblocking(True)
		else:
			self.SelectedDevice = None
		return self.SelectedDevice
	

	def WaitForDigEvents(self, AllowedEventLines, TimeoutMSecs):
		"""Wait for incoming digital events based on polling.

			Parameters:
				AllowedEventLines: bit mask [0-255] to select the digital input lines.
				TimeoutMSecs: timeout period in ms
   
			Returns:
		"""
		# flush the buffer!
		while (self.SelectedDevice.read(1) != []):
			continue
			
		TimeoutSecs = TimeoutMSecs / 1000
		startTime = time.time()		
		
		while 1:
			ElapsedSecs = (time.time()-startTime)
			lastbtn = self.SelectedDevice.read(1)		   
			if (lastbtn != []):
				if (lastbtn[0] & AllowedEventLines > 0):
					break
			# break for timeout:
			if (TimeoutMSecs != -1):
				if (ElapsedSecs >= (TimeoutSecs)):
					lastbtn = [-1]
					ElapsedSecs = TimeoutSecs
					break
		return lastbtn[0], round(1000.0 * ElapsedSecs)
		
	def GetAxis(self, ):
		"""GetAxis data.
        
            Parameters: -
            
            Returns: 

        """
		while (self.SelectedDevice.read(1) != []):
			pass
		time.sleep(.01)
		valueList = self.SelectedDevice.read(3)   
		if (valueList == []):
			return self.__AxisValue
		self.__AxisValue = valueList[1] + (256*valueList[2])
		
		return self.__AxisValue
	

	# Functions that only require a single USB command to be sent to the device.
	def SetLines(self, OutValue):
		"""Set output lines.
        
        	Parameters:
        		OutValue: bit pattern [0-255] to set the digital output lines.
		"""
		self.SelectedDevice.write([ 0, self.__SETOUTPUTLINES, OutValue, 0, 0, 0, 0, 0, 0, 0, 0 ])
		

	def PulseLines(self, OutValue, DurationInMillisecs):
		"""Pulse output lines.

            Parameters:
                OutValue: bit pattern [0-255] to pulse the digital output lines.
                DurationInMillisecs: sets the duration of the pulse.
		"""
		self.SelectedDevice.write([ 0, self.__PULSEOUTPUTLINES, OutValue, DurationInMillisecs & 255, DurationInMillisecs >> 8, 0, 0, 0, 0, 0, 0])
			  

	def SetAnalogEventStepSize(self, NumberOfSamplesPerStep):
		"""Set analog event step size.
        
            Parameters:
                NumberOfSamplesPerStep: set the number of samples per step.
		"""
		self.SelectedDevice.write([ 0, self.__SETANALOGEVENTSTEPSIZE, NumberOfSamplesPerStep, 0, 0, 0, 0, 0, 0, 0, 0 ])


	def RENC_SetUp(self, Range, MinimumValue, Position, InputChange, PulseInputDivider):
		"""Rotary Encoder setup.
        
            Parameters:
                Range:
                MinumumValue:
                Position:
                InputChange:
                PulseInputDivider:
		"""
		self.__AxisValue = Position
		self.SelectedDevice.write([ 0, self.__SETUPROTARYCONTROLLER, Range & 255, Range >> 8, MinimumValue & 255 , MinimumValue >> 8, Position & 255, Position >> 8, InputChange, PulseInputDivider, 0])
	

	def RENC_SetPosition(self, Position):
		"""Rotary Encoder set position.

            Parameters:
                Position: Set the current position.
		"""
		self.__AxisValue = Position
		self.SelectedDevice.write([ 0, self.__SETROTARYCONTROLLERPOSITION, Position & 255, Position >> 8, 0, 0, 0, 0, 0, 0, 0])
		
  
	def SetLedColor(self, RedValue, GreenValue, BlueValue, LedNumber, Mode):
		"""Set LED color.

            Parameters:
                RedValue:
                GreenValue:
                BlueValue:
                LedNumber:
                Mode:
        """
		self.SelectedDevice.write([ 0, self.__SETWS2811RGBLEDCOLOR, RedValue, GreenValue, BlueValue, LedNumber, Mode, 0, 0, 0, 0 ])
		

	def SendColors(self, NumberOfLeds, Mode):
		"""Set LED color.
        
            Parameters:
                RedValue:
                GreenValue:
                BlueValue:
                LedNumber:
                Mode:
        """
		self.SelectedDevice.write([ 0, self.__SENDLEDCOLORS, NumberOfLeds, Mode, 0, 0, 0, 0, 0, 0, 0 ])

	def Reset(self):
		"""Reset EVT device. WARNING! Will disconnect the USB.
        
		"""
		self.SelectedDevice.write([ 0, self.__RESET, 0, 0, 0, 0, 0, 0, 0, 0, 0 ])

   
	__AxisValue = 0
	
	# CONSTANTS:
	__CLEAROUTPUTPORT = 0# 0x00
	__SETOUTPUTPORT = 1   # 0x01
	__SETOUTPUTLINES = 2   # 0x02
	__SETOUTPUTLINE = 3   # 0x03
	__PULSEOUTPUTLINES = 4   # 0x04
	__PULSEOUTPUTLINE = 5   # 0x05

	__SENDLASTOUTPUTBYTE = 10   # 0x0A

	__CONVEYEVENT2OUTPUT = 20   # 0x14
	__CONVEYEVENT2OUTPUTEX = 21   # 0x15
	__CANCELCONVEYEVENT2OUTPUT = 22   # 0x16

	__CANCELEVENTREROUTES = 30   # 0x1E
	__REROUTEEVENTINPUT = 31   # 0x1F

	__SETUPROTARYCONTROLLER = 40# 0x28
	__SETROTARYCONTROLLERPOSITION = 41  # 0x29

	__CONFIGUREDEBOUNCE = 50   # 0x32

	__SETWS2811RGBLEDCOLOR = 60  # 0x3C
	__SENDLEDCOLORS = 61  # 0x3D

	__SWITCHALLLINESEVENTDETECTION = 100   # 0x64
	__SWITCHLINEEVENTDETECTION = 101   # 0x65

	__SETANALOGINPUTDETECTION = 102   # 0x66
	__REROUTEANALOGINPUT = 103# 0X67
	__SETANALOGEVENTSTEPSIZE = 104 # 0X68

	__SWITCHDIAGNOSTICMODE = 200   # 0xC8
	__SWITCHEVENTTEST = 201   # 0xC9

	__RESET = 255	# 0xFF

#-*- coding:utf-8 -*-

