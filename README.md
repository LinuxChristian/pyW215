# pyW215

pyW215 is a python3 library for interfacing with the d-link W215 Smart Plug.

The library is largely inspired by the javascript implementation by @bikerp [dsp-w215-hnap](https://github.com/bikerp/dsp-w215-hnap).

# Usage
```python
from pyW215 import SmartPlug

sp = SmartPlug('192.168.1.110', '******')

# Get values if available otherwise return N/A
print(sp.current_consumption)
print(sp.temperature)
print(sp.total_consumption)

# Turn switch on and off
sp.state = 'ON'
sp.state = 'OFF'
```

Note: You need to know the IP and password of you device. The password is written on the side.

# Working firmware versions
* v2.02
* v2.22

Note: If you experience problems with the switch first try upgrading to the latest supported firmware through the D-Link app. If the problem persists feel free to open an issue about the problem.

## Partial support
* v1.24 (State changing and current consumption working, but no support for reading temperature)
* D-Link W110 smart switch (only state changing is supported)

If you have it working on other firmware or hardware versions please let me know.
