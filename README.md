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

## Examples
```
from pyevt import EventExchanger
myevt = EventExchanger() # create device handle
myevt.attach('EventExchanger') # or 'EVT02', 'SHOCKER' or 'RSP-12', etc.
myevt.write_lines(0) # reset outputs
myevt.pulse_lines(170, 1000) # value=170, duration=1s
myevt.close_evt() # remove device handle

# reconnect RSP-12
myevt.attach('RSP-12')
myevt.wait_for_event(3, None) # wait for button 1 OR 2, timeout is infinite.
myevt.close_evt() # remove device handle
```