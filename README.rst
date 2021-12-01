pyW215
======

pyW215 is a python3 library for interfacing with the d-link W215 Smart
Plug.

The library is largely inspired by the javascript implementation by
@bikerp `dsp-w215-hnap`_.

Installing
==========
Install using the PyPI index

.. code:: bash

  pip install pyW215

Usage
=====

.. code:: python

   #!python3
   from pyW215.pyW215 import SmartPlug, ON, OFF

   sp = SmartPlug('192.168.1.110', '******')
   # Where ****** is the "code pin" printed on the setup card

   # Get values if available otherwise return N/A
   print(sp.current_consumption)
   print(sp.temperature)
   print(sp.total_consumption)

   # Turn switch on and off
   sp.state = ON
   sp.state = OFF

Note: You need to know the IP and password of your device. The password is written on the side.

Contributions
=========================
I personally no longer use my W215 but contributions are always welcome. **If you do submit a PR please ping @LinuxChristian.** If I don't respond within a few days just ping me again.

Working firmware versions
=========================

-  v2.02
-  v2.03
-  v2.22

Note: If you experience problems with the switch upgrade to the latest supported firmware through the D-Link app. If the problem persists feel free to open an issue about the problem.

Partial support
---------------

-  v1.24 and v1.25 (State changing and current consumption working, but no support for reading temperature)
-  D-Link W110 smart switch D-Link W110 smart switch (only state viewing and changing is supported)

If you have it working on other firmware or hardware versions please let me know.

Need support for W115 or W245?
-------------------------------
Checkout this library, https://github.com/jonassjoh/dspW245

.. _dsp-w215-hnap: https://github.com/bikerp/dsp-w215-hnap


Need support for W218
-------------------------------
DSP-W218 uses `a completly different protocol <https://github.com/LinuxChristian/pyW215/issues/38#issuecomment-980794946>`_ compare to earlier versions. There is no roadmap to add support for W218 but PR's are always welcome.
