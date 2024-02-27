#!/usr/bin/env python
""" \example XEP_X4M200_X4M300_plot_record_playback_radar_raw_data.py

#Target module: X4M200,X4M300,X4M03

#Introduction: XeThru modules support both RF and baseband data output. This is an example of radar raw data manipulation. 
               Developer can use Module Connecter API to read, record radar raw data, and also playback recorded data. 
			   
#Command to run: "python XEP_X4M200_X4M300_plot_record_playback_radar_raw_data.py -d com8" or "python3 X4M300_printout_presence_state.py -d com8"
                 change "com8" with your device name, using "--help" to see other options.
                 Using TCP server address as device name is also supported, e.g. 
                 "python X4M200_sleep_record.py -d tcp://192.168.1.169:3000".
"""

from __future__ import print_function, division

import sys
from optparse import OptionParser
from time import sleep

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import pymoduleconnector
from pymoduleconnector import DataType


__version__ = 3
global FPS
FPS = 20

def reset(device_name):
    mc = pymoduleconnector.ModuleConnector(device_name)
    xep = mc.get_xep()
    xep.module_reset()
    mc.close()
    sleep(3)

def clear_buffer(xep):
    """Clears the frame buffer"""
    while xep.peek_message_data_float():
        xep.read_message_data_float()
def configure(device_name):
    global FPS

    reset(device_name)
    mc = pymoduleconnector.ModuleConnector(device_name)

    # Assume an X4M300/X4M200 module and try to enter XEP mode
    app = mc.get_x4m300()
    # Stop running application and set module in manual mode.
    try:
        app.set_sensor_mode(0x13, 0) # Make sure no profile is running.
    except RuntimeError:
        # Profile not running, OK
        pass

    try:
        app.set_sensor_mode(0x12, 0) # Manual mode.
    except RuntimeError:
        # Maybe running XEP firmware only?
        pass

    xep = mc.get_xep()
    # Set DAC range
    xep.x4driver_set_dac_min(900)
    xep.x4driver_set_dac_max(1150)

    # Set integration
    xep.x4driver_set_iterations(16)
    xep.x4driver_set_pulses_per_step(26)

    xep.x4driver_set_downconversion(0)
    # Start streaming of data
    xep.x4driver_set_fps(FPS)

    return xep

def read_frame(xep):
    """Gets frame data from module"""
    d = xep.read_message_data_float()
    frame = np.array(d.data)
    return frame

def simple_xep_plot(device_name):
    global FPS
    reset(device_name)
    xep = configure(device_name)

    def animate(i):
        line.set_ydata(read_frame())
        return line,

    fig = plt.figure()
    fig.suptitle("example version %d "%(__version__))
    ax = fig.add_subplot(1,1,1)
    ax.set_ylim(-0.03,0.03) #keep graph in frame (FIT TO YOUR DATA)
    frame = read_frame(xep)
    line, = ax.plot(frame)

    clear_buffer(xep)

    ani = FuncAnimation(fig, animate, interval=FPS)
    try:
        plt.show()
    finally:
        # Stop streaming of data
        xep.x4driver_set_fps(0)
    
def simple_xep(device_name):

    xep = configure(device_name)
    clear_buffer(xep)
    try:
        while True: 
            frame = read_frame(xep)
            print(len(frame))
            clear_buffer(xep)
    except KeyboardInterrupt:
        print("Interrupted")
    
    # Stop streaming of data
    xep.x4driver_set_fps(0)

def main():
    parser = OptionParser()
    parser.add_option(
        "-d",
        "--device",
        dest="device_name",
        help="device file to use",
        metavar="FILE")
    
    parser.add_option(
        "-v",
        "--visualize",
        dest="vis",
        default=False,
        help="visualize true/false")

    (options, args) = parser.parse_args()
    if not options.device_name:
        parser.error("Missing -d See --help.")
    else:
        if options.vis:
            simple_xep_plot(options.device_name)
        else:
            simple_xep(options.device_name)

def read_UWBdata(device_name):
    simple_xep(device_name)

if __name__ == "__main__":
   main()
