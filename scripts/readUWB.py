#!/usr/bin/env python

from python27.pymoduleconnector.examples.rawreadings import *
from optparse import OptionParser
import rospy
from x4m300.msg import FloatList

def main():
    print("\nWaiting for UWB...")
    pub = rospy.Publisher('readings', FloatList, queue_size=10)
    rospy.init_node('UWBtalker', anonymous=True)

    hz = rospy.get_param('/pubRate')
    rate = rospy.Rate(hz) # e.g. 10hz
    
    parser = OptionParser()
    parser.add_option(
        "-d",
        "--device",
        dest="device_name",
        help="device file to use")

    (options, args) = parser.parse_args()

    if not options.device_name:
            parser.error("Missing -d See --help.")
    else:
        xep = configure(options.device_name)
        clear_buffer(xep)

        data2send = FloatList()
        print('\nStarted publishing data...! ' + options.device_name)
        try:
            while not rospy.is_shutdown():
                clear_buffer(xep)
                frame = read_frame(xep)
                # rospy.loginfo(frame)
                data2send.data = frame
                pub.publish(data2send)
                rate.sleep()
        except KeyboardInterrupt:
            print("Interrupted")

        # Stop streaming of data
        xep.x4driver_set_fps(0)

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
