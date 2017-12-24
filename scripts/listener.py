#!/usr/bin/env python
import rospy
from launchpad_ctrl.msg import LaunchpadKey


def callback(data):
  rospy.loginfo(rospy.get_caller_id() + "I heard %d %d %s", data.x, data.y, data.type)


def listener():
  # In ROS, nodes are uniquely named. If two nodes with the same
  # node are launched, the previous one is kicked off. The
  # anonymous=True flag means that rospy will choose a unique
  # name for our 'listener' node so that multiple listeners can
  # run simultaneously.
  rospy.init_node('listener', anonymous=True)

  rospy.Subscriber("launchpad_key_event", LaunchpadKey, callback)

  # spin() simply keeps python from exiting until this node is stopped
  rospy.spin()


if __name__ == '__main__':
  listener()
