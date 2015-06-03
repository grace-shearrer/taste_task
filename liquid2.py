"""
deliver juice
"""
#####to run, in shell window <execfile("liquid2.py")>, it initially doesn't work run via gui, then close and run cmdline#####
import psychopy.app
import numpy as N
import sys,os,pickle
################################################
#this is a unc edit, changed this path
sys.path.insert(0, '/Users/kylesburger/Desktop/taste_task/pyserial-2.6')
#####THIS IS IMPORTANT DON'T MESS WITH IT#######
sys.path.append('/Users/kylesburger/Desktop/taste_task')
import cv2
import syringe_pump
from psychopy import visual, core, event, logging, data, misc, sound

import socket
from socket import gethostname
import inspect
sys.path.append('/Users/kylesburger/Desktop/taste_task/')

import exptutils
from exptutils import *

import datetime

def store_scriptfile():
    scriptfile= inspect.getfile(inspect.currentframe())# save a copy of the script in the data file
    f=open(scriptfile)
    script=f.readlines()
    f.close()
    return script

def check_for_quit(subdata,win):
    k=event.getKeys()
    print 'checking for quit key %s'%subdata['quit_key']
    print 'found:',k
    if k.count(subdata['quit_key']) >0:# if subdata['quit_key'] is pressed...
        print 'quit key pressed'
        return True
    else:
        return False

def wait_for_trigger():
    event.clearEvents()
    if subdata['simulated_response']:
        msg="SIMULATION MODE"
    else:
        msg=''
    message=visual.TextStim(win, text='%s Waiting for start key (or press %s)\nBe very still!'%(msg,subdata['start_key']),
    font='BiauKai', height=1,color=u'white', colorSpace=u'rgb', opacity=1,depth=0.0,
    alignHoriz='center',wrapWidth=50)
    message.setAutoDraw(True) #automatically draw every frame
    win.flip()
    start=False
    while start==False:
        k=event.waitKeys()
        if k.count(subdata['start_key'])>0:#as soon as subdata['start_key'] is pressed...
            start=True
            message.setText('')#this clears the screen
            win.flip()
        if k.count(subdata['quit_key']) >0:# if subdata['quit_key'] is pressed...
            exptutils.shut_down_cleanly(subdata,win)
            return False
    return True

subdata={}
#subdata['subcode']='test'
subdata['subcode']=raw_input('subject id: ')

# initialize subdata dictionary to store info about the study
subdata['completed']=0
subdata['cwd']=os.getcwd()
subdata['hostname']=socket.gethostname()
clock=core.Clock()
datestamp=datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
subdata['datestamp']=datestamp
subdata['expt_title']='tampico_probabilistic'
subdata['script']=store_scriptfile()
subdata['response']={}
subdata['score']={}
subdata['rt']={}
subdata['stim_onset_time']={}
subdata['stim_log']={}
subdata['is_this_SS_trial']={}
subdata['SS']={}
subdata['broke_on_trial']={}

subdata['start_key']='5'
subdata['quit_key']='q'

subdata['simulated_response']=False

dataFileName='Output/%s_%s_subdata.log'%(subdata['subcode'],subdata['datestamp'])
logging.console.setLevel(logging.INFO)
logfile=logging.LogFile(dataFileName,level=logging.DATA)


try:
    print 'initializing serial device:'
    dev=syringe_pump.SyringePump('/dev/tty.USA19H142P1.1')
    print dev
    print 'using serial device: ', dev
    if not dev.isOpen():
        raise Exception('noPump')
    hasPump=True
except:
    hasPump=False


#from new_era import PumpInterface
#pi = PumpInterface(port='/dev/tty.usbserial')

# deliver 0.5 ml over 5 seconds
# equates to

diameter=26.59
mls_to_deliver=0.5
delivery_time=2.0
cue_time=2.0
wait_time=2.0
rinse_time=2.0
swallow_time=2.0
trial_length=cue_time+delivery_time+wait_time+rinse_time+swallow_time

rate = mls_to_deliver*(3600.0/delivery_time)  # mls/hour

trialcond=N.zeros(24).astype('int')

trialcond[0:8]=0     # water cue, water delivery
trialcond[8:12]=1    # water cue, juice delivery
trialcond[12:20]=2   # juice cue, juice delivery
trialcond[20:24]=3   # juice cue, water delivery
stim_images=['bottled_water.jpg','bottled_water.jpg','tampico.jpg','tampico.jpg']
ntrials=len(trialcond)
pump=N.zeros(ntrials)

N.random.shuffle(trialcond)

# pump zero is neutral, pump 1 is juice

pump[trialcond==1]=1
pump[trialcond==2]=1



onsets=N.arange(0,ntrials*trial_length,step=trial_length)


# clear infusion measurements
if hasPump:
    commands_to_send=['0PHN01','1PHN01','0CLDINF','1CLDINF','0DIRINF','1DIRINF','0RAT%0.1fMH'%rate,'1RAT%0.1fMH'%rate,'0VOL%0.1f'%mls_to_deliver,'1VOL%0.1f'%mls_to_deliver,'0DIA%0.1fMH'%diameter,'1DIA%0.1fMH'%diameter]
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

fullscr=False

win = visual.Window([800,600],allowGUI=True, fullscr=fullscr, monitor='testMonitor', units='deg')
visual_stim=visual.ImageStim(win, image=N.zeros((300,300)), size=(0.75,0.75),units='height')

event.clearEvents()
wt=wait_for_trigger()
if not wt:
    print 'quit button pressed!'
    sys.exit()
else:
    print "quit status:",wt
    
message=visual.TextStim(win, text='')

subdata['trialdata']={}
clock.reset()
event.clearEvents()

for trial in range(ntrials):
    if check_for_quit(subdata,win):
        exptutils.shut_down_cleanly(subdata,win)
        sys.exit()

    trialdata={}
    print 'trial %d'%trial
    trialdata['onset']=onsets[trial]
    print 'condition %d'%trialcond[trial]
    logging.log(logging.DATA,"Condition: %d"%trialcond[trial])
    print 'showing image: %s'%stim_images[trialcond[trial]]
    visual_stim.setImage(stim_images[trialcond[trial]])
    visual_stim.draw()
    logging.log(logging.DATA, "image=%s"%stim_images[trialcond[trial]])
    while clock.getTime()<trialdata['onset']:#wait until the specified onset time to display image_file
        if check_for_quit(subdata,win):
            exptutils.shut_down_cleanly(subdata,win)
            sys.exit()
    win.flip()

    while clock.getTime()<(trialdata['onset']+cue_time):#show the image
        pass

    if hasPump:
        print 'injecting via pump at address %d'%pump[trial]
        logging.log(logging.DATA,"injecting via pump at address %d"%pump[trial])

        dev.sendCmd('%dRUN'%pump[trial])
    else:
        print 'no pump: should be injecting via pump at address %d'%pump[trial]

    while clock.getTime()<(trialdata['onset']+cue_time+delivery_time):#wait until liquid is delivered
        pass
    message=visual.TextStim(win, text='')
    message.draw()
    win.flip()
    if hasPump:
        trialdata['dis']=[dev.sendCmd('0DIS'),dev.sendCmd('1DIS')]


    while clock.getTime()<(trialdata['onset']+cue_time+delivery_time+wait_time):
        pass

    if hasPump:
        print 'injecting rinse via pump at address %d'%0
        dev.sendCmd('%dRUN'%0)
    else:
        print 'no pump: should be injecting rinse via pump at address %d'%pump[trial]

    while clock.getTime()<(trialdata['onset']+cue_time+delivery_time+wait_time+rinse_time):
        pass

    message=visual.TextStim(win, text='swallow')
    message.draw()
    win.flip()

    while clock.getTime()<(trialdata['onset']+cue_time+delivery_time+wait_time+rinse_time+swallow_time):
        pass
    message=visual.TextStim(win, text='')
    message.draw()
    win.flip()

    while clock.getTime()<(trialdata['onset']+trial_length):
        pass

    subdata['trialdata'][trial]=trialdata           

win.close()

#print dev.sendCmd('VER')
f=open('Output/liquid_subdata_%s.pkl'%datestamp,'wb')
pickle.dump(subdata,f)
f.close()
