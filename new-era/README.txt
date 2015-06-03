Welcome to New Era Pump Interface's documentation!
==================================================

This was written by Brad Buran (bburan@alum.mit.edu) for a project in Dan Sanes'
lab at the Center for Neural Science, New York University.  The code is licensed
under the GPL v3 (see LICENSE.txt).

A copy can be obtained from Bitbucket (http://bitbucket.org/bburan/new-era).
An HTML version of the docs can be found at
http://new-era-pump.readthedocs.org.  Bug reports, patches and enhancements are
welcome.

Although I have only tested this with the model we use (NE-1000), I believe this
will work with the majority of the pumps created by the manufacturer.  We are
*not* affiliated with New Era Pump Systems.

Overview
--------

Most of New Era's pumps can be controlled via a series of commands sent via the
RS-232 interface.  This module handles much of the low-level operations required
to communicate with the pump (e.g. opening the serial port, encoding the command
into a request packet and parsing the resulting response packet, raising an
exception when the pump stalls or fails to process a command).

Getting started
---------------

This module requires PySerial.  Although it may be possible to establish a
RS-232 connection via USB, this module only supports serial (COM) ports at the
moment.  If you have multiple serial ports (unlikely with newer computers), make
a note of which port you use.  PySerial numbers the ports starting at 0 (e.g.
the first port is 0, second port is 1, etc.). 

Launch your Python shell and connect to the pump

>>> from new_era import PumpInterface
>>> pi = PumpInterface()

Note that PumpInterface defaults to the first COM port.  If the pump is
connected to a different port (e.g. the second one), you need to specify the
port to use.

>>> pi = PumpInterface(port=1)

Once connected, you may transmit commands directly to the pump.  For a list of
commands supported by the firmware, see the documentation provided by the
vendor (New Era Pump Systems).

>>> pi.xmit('VOL ML')
>>> pi.xmit('VOL 3.0')

Alternatively, you can transfer an entire sequence of commands.

>>> pi.xmit_sequence('VOL ML', 'VOL 3.0', 'TRG T2', 'RUN')

Or, you can use several convenience methods provided.  See the API documentation
(at the end of this page) for a list of the methods available.

>>> pi.set_trigger(start='rising', stop=None)

Note that `set_trigger` allows you define the start and stop conditions.  The
pump trigger is then set to the appropriate mode.  Not all start/stop conditions
are supported by the pump firmware (e.g. you cannot have the pump start and stop
on a rising edge).

Handling units
--------------

The default units for (ml/m) rate and volume (ml) are defined when you create
the interface.  Rate units can be ul/min, ul/h ml/min or ml/h.  Volume units can
be ml or ul.  By default, methods that deal with rate or volume (e.g. `set_rate`,
`set_volume`, `get_infused` and `get_withdrawn`) will assume that values are
provided in these units.

>>> pi = PumpInterface(rate_unit='ml/h', volume_unit='ul')
>>> pi.set_rate(0.3)    # assumes value is in ml/h
>>> pi.set_volume(0.03) # assumes value is in ul
>>> pi.run()
>>> print pi.get_infused()

You can provide values in a different unit if desired.  Only conversions between
the allowable units listed above are supported (more units can be added in the
future if desired).

>>> pi.set_rate(300, unit='ul/h')
>>> pi.set_volume(0.00003, unit='ml')
>>> print pi.get_infused(unit='ul')

Note that the units used for communicating with the pump are defined when the
interface is created.  From that point, all needed unit conversions are handled
in the Python layer.  In the example below, the pump firmware expects all volume
information to be in ml.  The request to set volume is converted from 3000 ul to 
3 ml before being passed to the pump.  When using this feature, it's important
to keep in mind that the RS-232 interface may not support a large number of
significant figures, so you should set the default volume and rate units
appropriately (e.g. if you want to deal with volumes less than 1 ul, don't set
the default volume unit to ml).  

>>> pi = PumpInterface(volume_unit='ml')
>>> pi.set_volume(3000, unit='ul')
