# pyW215

pyW215 is a python3 library for interfacing with the d-link W215 Smart Plug.

The library is largely inspired by the javascript implementation by @bikerp [dsp-w215-hnap](https://github.com/bikerp/dsp-w215-hnap).

# Usage
```python
 from pyW215 import SmartPlug

 sp = SmartPlug('192.168.1.110', '******')
 cc = sp.current_consumption
 print(cc)
```

Note: You need to know the IP and password of you device. The password is written on the side.

# Working firmware versions
* v2.02
* v2.22

## Partial support
* v1.24 (State changing working, but fails to read temperature or current consumption)

If you have it working on other firmware versions please let me know.
