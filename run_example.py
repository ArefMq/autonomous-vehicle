#!/usr/bin/env python
from brain import Brain
import cv2

brain = Brain()


image = cv2.imread('img8.jpg')
steering_command = brain.process(image)

print('Steering Command: %f' % steering_command)
print('Average Cycle Time: %.0f ms' % (brain.average_cycle_time * 1000))
