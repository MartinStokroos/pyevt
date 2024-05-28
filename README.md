# pyevt - A python package for the Event-Exchanger EVT-2 USB hardware

## 1. About

This repository contains the code to communicate with *EVT-2* USB-devices, developed by the Research Support group of the faculty of Behavioral and Social Science from the University of Groningen. This code was originally written by Eise Hoekstra and Mark M. Span and is now maintained by Martin Stokroos

The *EVT-2* is an event marking and triggering device intended for physiological experiments.
*pyevt* is a Python module to communicate with *EVT-2* hardware (+derivatives).

### Install
Install pyevt with:

`pip install pyevt` or
`pip install --user pyevt` on managed computers.

### Dependencies
*pyevt* uses the *HIDAPI* python module to communicate over USB according the HID class.
![https://pypi.org/project/hidapi/](https://pypi.org/project/hidapi/)

- Linux
In Linux (Ubuntu), permission for using EVT (HID) devices should be given by adding the next lines in a file, for example,  named: `99-evt-devices.rules` in `/etc/udev/rules.d`:

```
# /etc/udev/rules.d/99-evt-devices.rules

# All EVT devices
SUBSYSTEM=="usb", ATTR{idVendor}=="0004", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0008", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0009", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0114", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0208", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0308", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0408", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0508", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0604", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0808", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="0909", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="1803", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="1807", MODE="0660", GROUP="plugdev"
```

The user should be member of the `plugdev` -group.

### Code Examples
```
from pyevt import EventExchanger
myevt = EventExchanger() # create device handle
myevt.scan('partial_device_name') # Get list of devices containing partial string. Default is 'EventExchanger'.
myevt.attach_name('partial_device_name') # Example: 'EVT02', 'SHOCKER' or 'RSP-12', etc. The default is 'EventExchanger'.

myevt.write_lines(0) # clear outputs
myevt.pulse_lines(170, 1000) # value=170, duration=1s

myevt.close() # remove device handle

# reconnect RSP-12
myevt.attach('RSP-12')
myevt.wait_for_event(3, None) # wait for button 1 OR 2, timeout is infinite.
myevt.close() # remove device handle
```

## 2. LICENSE
The evt-plugins collection is distributed under the terms of the GNU General Public License 3.
The full license should be included in the file COPYING, or can be obtained from

[http://www.gnu.org/licenses/gpl.txt](http://www.gnu.org/licenses/gpl.txt)

This plugin collection contains the work of others.

## 3. Documentation
EVT-devices and plugin information:

[https://markspan.github.io/evtplugins/](https://markspan.github.io/evtplugins/)