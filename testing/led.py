# import RPi.GPIO as GPIO											#	10/28/2020
# GPIO.setmode(GPIO.BCM)											#	10/28/2020
# PIR_sensor = 17														#	10/28/2020
# # sensor = 18														#	10/28/2020
# GPIO.setup(PIR_sensor, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)		#	10/28/2020


import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led1 = 26       #   Green
led2 = 27       #   Red
GPIO.setup( led1, GPIO.OUT)
print "LED on"
GPIO.output( led1, GPIO.HIGH)
time.sleep(1)
print "LED off"
GPIO.output( led1, GPIO.LOW)
