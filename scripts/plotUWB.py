#!/usr/bin/env python

from python27.pymoduleconnector.examples.rawreadings import *
from optparse import OptionParser
import rospy
from x4m300.msg import FloatList
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

global xlims
xlims = rospy.get_param('/xLims')

class Visualiser:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        plt.ylabel("normalized amplitudes")
        plt.xlabel("bins")
        plt.grid()
        self.ln, = plt.plot([], [])
        self.x_data, self.y_data = [] , []

    def plot_init(self):
        self.ax.set_xlim(xlims[0], xlims[1])
        self.ax.set_ylim(-0.03, 0.03)
        return self.ln

    def UWBcallback(self, msg):
        global xlims
        frame = msg.data
        self.y_data = frame[xlims[0]:xlims[1]]
        self.x_data = range(xlims[0], xlims[1])
    
    def update_plot(self, frame):
        self.ln.set_data(self.x_data, self.y_data)
        return self.ln


vis = Visualiser()

def main():
    print("\nWaiting for plotting...")
    parser = OptionParser()
    parser.add_option(
        "-t",
        "--topic",
        dest="topic_name",
        help="device file to use")

    (options, args) = parser.parse_args()

    rospy.init_node('UWBlistener', anonymous=True)
    rospy.Subscriber(options.topic_name, FloatList, vis.UWBcallback)

    if not options.topic_name:
            parser.error("Missing -d See --help.")
    else:
        try:
            ani = FuncAnimation(vis.fig, vis.update_plot, init_func=vis.plot_init)
            vis.fig.suptitle(options.topic_name)
            plt.show(block=True) 
        except KeyboardInterrupt:
            plt.close('all')
            print('Thanks for plotting')

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        plt.close('all')
        pass
