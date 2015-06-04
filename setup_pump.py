"""
set up pump
"""

import numpy as N
import syringe_pump
from psychopy import visual, core, event, logging, data, misc, sound
import os
import socket
from socket import gethostname
import inspect
import exptutils
from exptutils import *

import datetime

execfile("syringe_pump.py")

subdata={}

try:
    print 'using serial device: ', dev
    if not dev.isOpen():
        raise Exception('noPump')
    print 'initializing serial device:'
    dev=syringe_pump.SyringePump('/dev/tty.KeySerial1')
    print dev
    hasPump=True
except:
    raise BaseException('no pump detected!')


#from new_era import PumpInterface
#pi = PumpInterface(port='/dev/tty.usbserial')

# deliver 0.5 ml over 5 seconds
# equates to

diameter=26.59
mls_to_deliver=0.5
delivery_time=4.0
cue_time=4.0
rate = 7.5  # mls/hour


# clear infusion measurements
if hasPump:
    commands_to_send=['0PHN01','1PHN01','0CLDINF','1CLDINF','0DIRINF','1DIRINF','0RAT%0.1fMH'%rate,'1RAT%0.1fMH'%rate,'0VOL%0.1f'%mls_to_deliver,'1VOL%0.1f'%mls_to_deliver,'0DIA%0.1fMH'%diameter,'1DIA%0.1fMH'%diameter]
#this is the only place we see pumpver
    subdata['pumpver']=dev.sendCmd('VER')

    dev.setBaudrate(9600)

    for cmd in commands_to_send:
        print 'sending: ',cmd
        dev.sendCmd(cmd)
        core.wait(0.1)

    subdata['pumpdata']={}
    for p in [0,1]:
        for cmd in ['DIS','DIR','RAT','VOL','DIA']:
            fullcmd='%d%s'%(p,cmd)
            subdata['pumpdata'][fullcmd]=dev.sendCmd(fullcmd)
            core.wait(0.1)

    print subdata['pumpdata']

# setup screen
print ('diameter')
print('rate')
print ('mls_to_deliver')
print 'done tacocat'