# pyevt - A python package for the Event Exchanger EVT-2 USB hardware
This repository contains the code to communicate with the *EVT-2* USB devices developed by the Research Support group of the faculty of Behavioral and Social Science from the University of Groningen. This code was originally written by Eise Hoekstra and Mark M. Span and is now maintained by Martin Stokroos and Mark M. Span

## Purpose
The *EVT-2* is an event marking and triggering device intended for physiological experiments.
*pyevt* is a Python module to communicate with *EVT-2* hardware (+derivatives).

## Dependencies
pyevt uses the *HIDAPI* python module to communicate over USB according the HID class.
https://pypi.org/project/hidapi/

## Usage
Install pyevt with:

`pip install pyevt` or
`pip install --user pyevt` on managed computers.

## Example
```
from pyevt import EvtExchanger
myevt = EvtExchanger()
myevt.Select("EventExchanger")

myevt.SetLines(0) # reset outputs
myevt.PulseLines(170, 1000) # value=170, duration=1s

del myevt # remove device handle
```