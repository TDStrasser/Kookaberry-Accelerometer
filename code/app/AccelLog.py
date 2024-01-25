# File name: 
__name__ = 'AccelLog'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 31 March 2021
# Date last modified: 29 November 2023 - implement pre-acceleration recording buffer, bug-fixes
# MicroPython Version: 1.20 for the Kookaberry RP2040 mini-accelerometer board
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
# To the fullest extent permitted by law, AustSTEM absolutely disclaims 
# all warranties, expressed or implied, including, but not limited to, 
# implied warranties of merchantability and fitness for any particular purpose. 
# AustSTEM gives no warranty that this software will be free of errors, 
# or that defects in the software will be corrected,  
# See the GNU General Public License for more details.
#
# Measures and logs 3-axis acceleratins using the built-in accelerometer
# The app starts and waits to be armed with the ORANGE LED ON
# Press the button to arm the logger - the ORANGE LED is OFF and the RED LED is ON
# When armed the logger waits for high acceleration in any direction
# When detected acceleration is logged at 10mS intervals for 5 seconds. The RED LED blinks during logging.
# Sequentially named files are created for each run in the form AccelLog-nnn.CSV wher nnn is the run number.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: nil
# /lib files: Nil
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: Spreadsheet program on PC
#------------------------------------------
# Begin code
# Initial conditions

DURATION = 5 # The logging duration in seconds
PERIOD = 10 # The period between samples in milliseconds
THRESHOLD = 20 # The threshold acceleration in m/sec^2 which initiates logging when armed
PRESAMPLES = 10 # The number of samples retained prior to reaching the recording threshhold

import kooka, machine, os, re, json, time

# Set up the button class to keep track of button activity
class Button:
    def __init__(self, gpio):
        self.button = machine.Pin(gpio, machine.Pin.IN) # define the button object
        self.state = self.button.value()
        self.btn_count = 0 # number of times pressed
        self.button.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.process_button)
        
    def process_button(self, b):
        time.sleep_ms(2) # Wait for button debounce
        btnval = self.button.value()
        if self.state == True and btnval == False: # 1 to 0 transition?
            self.btn_count += 1
        self.state = btnval
#        print(self.state, self.btn_count)
        
    def is_pressed(self):
        return not self.state
        
    def was_pressed(self):
        pressed = self.btn_count > 0 # Whether there are presses
        self.btn_count = max(0, self.btn_count - 1) # dequeue button presses
        return pressed
        
    def get_presses(self):
        return self.btn_count
       
btn = Button('P1') # The control button on the board
LD1 = machine.Pin('P4', machine.Pin.OUT) # Red LED
LD1.value(0)
LD2 = machine.Pin('P2', machine.Pin.OUT) # Orange LED
LD2.value(1)

disp = kooka.display    # initialise the OLED display
# params = config('Kappconfig.txt')   # read the configuration file

kooka.accel.config(freq=100, range=8) # Set up the accelerometer range (in g) and sampling rate (in Hz)


# set up for the datalogger - file name is AccelLog-r.csv where r is the run number
p = re.compile(r'\W+')     # regular expression to split strings into alphanumeric words
flist = os.listdir('/')    # fetch the full list of files
run = 0    # Initialise the run number
for i in range(0,len(flist)):    # examine each directory entry
    entry = p.split(flist[i],4)    # split the entry into words
    if len(entry) == 3 and entry[0] == __name__ and entry[2].lower() == 'csv':
        run = max(run, int(entry[1]))    # Find the last used run number

# Set up the state machine
# 0 is the quiescent state
# 1 is the armed state
# 2 is the measuring and logging state
# 3 is the run cleanup state which return to state 0
state = 0
acc_interval = PERIOD    # milliseconds between accelerometer reads
acc_samples = int(DURATION * 1000 / acc_interval) + 1   # Number of acceleration measurements to be gathered when triggered
timer_acc = time.ticks_ms()    # timer used for timing readings
timer_zero = time.ticks_ms()    # time at which logging began
timer_run = 0
PRESAMPLES +=1 # Needs one extra sample to retain the number of samples specified

# Set up the sample data buffers
acc_x = [0] * acc_samples # x axis
acc_y = [0] * acc_samples # y axis
acc_z = [0] * acc_samples # z axis
acc_t = [0] * acc_samples # sample times

pre_x = [0] * PRESAMPLES # x axis
pre_y = [0] * PRESAMPLES # y axis
pre_z = [0] * PRESAMPLES # z axis
pre_t = [0] * PRESAMPLES # sample times

sample_ptr = 0
pre_samples = 0
accel = (0,0,0)    # Initialise acceleration readings

while True: # Runs forever
# Read and process the accelerometer
    if time.ticks_diff(time.ticks_ms(), timer_acc) >= 0:
        accel = kooka.accel.get_xyz()
#        sample_time = int(time.ticks_diff(time.ticks_ms(), timer_zero))
        sample_time = time.ticks_ms()
        if state == 1:    # when armed
            if sample_ptr >= PRESAMPLES: # Initially fill the buffer then shift all the samples along and then record the latest
                for i in range(1,PRESAMPLES):
                    pre_t[i-1] = pre_t[i]
                    pre_x[i-1] = pre_x[i]
                    pre_y[i-1] = pre_y[i]
                    pre_z[i-1] = pre_z[i]
                sample_ptr -= 1 # adjust presample buffer pointer
            pre_t[sample_ptr] = sample_time # Record sample time in absolute ticks
            pre_x[sample_ptr] = accel[0]
            pre_y[sample_ptr] = accel[1]
            pre_z[sample_ptr] = accel[2]
            sample_ptr += 1
            pre_samples = sample_ptr # Remember how many presamples were recorded
        elif state == 2:    # when triggered
            acc_t[sample_ptr] = sample_time # Record sample time
            acc_x[sample_ptr] = accel[0]
            acc_y[sample_ptr] = accel[1]
            acc_z[sample_ptr] = accel[2]
            sample_ptr += 1
            timer_run = int(sample_time / 1000)
    # Blink the LED
            if sample_time % 32 < 16: LD1.value(not LD1.value())
     # set up for next sample
        timer_acc += acc_interval
# Manage the states
    if btn.was_pressed(): # Arms or disarms the logger
        if state == 0:    # Arms the logger
            state = 1
            LD1.value(1)
            LD2.value(0)
            sample_ptr = 0
            for i in range(0,PRESAMPLES): # Clear the pre-sampling buffer
                pre_t[i-1] = 0
                pre_x[i-1] = 0
                pre_y[i-1] = 0
                pre_z[i-1] = 0
                
        elif state == 1:    # Disarms the logger
            state = 0
            LD1.value(0)
            LD2.value(1)
        elif state == 2:    # Resets the logging phase to armed
            state = 1
            LD1.value(1)
            LD2.value(0)
        elif state == 3:    # End of run state
            state = 0
            LD1.value(0)
            LD2.value(1)
    # Detect large acceleration in any direction
    if (abs(min(accel)) > THRESHOLD or max(accel) > THRESHOLD) and state == 1: # if a large acceleration in any direction
        state = 2    # Start logging
        for i in range(0, acc_samples): 
            acc_t[i] = 0 #Reset all data
            acc_x[i] = 0 #Reset all data
            acc_y[i] = 0 #Reset all data
            acc_z[i] = 0 #Reset all data
        timer_zero = sample_time    # initialise logging timer
        timer_run = 0
        sample_ptr = 0

    # End the logging run
    if state == 2 and sample_ptr >= acc_samples:
        # print('Run ended')
        state = 3    # Progress to review state
        LD1.value(1)
        LD2.value(1)

        # Log data to the file
        run += 1    # Increase the run number
        fname = __name__ + '-%0.3d.csv' % run
        f = open(fname, 'w+')
        f.write('Time-ms, X_Acc-m/sec2, Y_Acc-m/sec2, Z_Acc-m/sec2\n')   # write the heading line
        for i in range(0, pre_samples): # First write the presampling data
            f.write('%d,%0.2f,%0.2f,%0.2f\n' % (int(time.ticks_diff(pre_t[i], timer_zero)), pre_x[i], pre_y[i], pre_z[i]))
#            f.write('%d,%0.2f,%0.2f,%0.2f\n' % (pre_t[i], pre_x[i], pre_y[i], pre_z[i]))
        for i in range(0, acc_samples):
            f.write('%d,%0.2f,%0.2f,%0.2f\n' % (int(time.ticks_diff(acc_t[i], timer_zero)), acc_x[i], acc_y[i], acc_z[i]))
        f.close()
