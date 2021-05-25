#	LoRa.py
#	TKinter, LoRa

#	697	Networks
#	Final Project
#	Sam Portillo
#	May Day 2019

#	References:
#		GUI & Multithreading	→	https://www.youtube.com/watch?v=_p3EezlvcGs&t=778s
#		OpenCV					→	https://www.youtube.com/watch?v=_aTC-Rc4Io0&t=212s
#		OpenCV					→	https://www.youtube.com/watch?v=BDt0-F3PL8U&t=170s
#		Servo					→	https://www.youtube.com/watch?v=ddlDgUymbxc
#		GPIO					→	https://sourceforge.net/p/raspberry-gpio-python/wiki/PWM/
#		https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
#		https://stackoverflow.com/questions/38645060/what-is-the-equivalent-of-serial-available-in-pyserial
#		https://pyserial.readthedocs.io/en/latest/pyserial_api.html
#		sudo apt-get install rpi.gpio		Does not workon
#		pip  install RPi.GPIO				For python 2.7
#		pip3 install RPi.GPIO				For python 3.5
#		dpkg --get-selections		List installed modules
#		https://www.youtube.com/watch?v=9pn1KKhxwdM		Apache
#		python -m pip install pyserial

#	Setup:
#		Baybox	morningfishliveshineturnwas
#		sudo service motion stop  →	If you have motion installed then you will need to stop the service
#									If the camera's blue light is on then the motion service is active.
#		lsusb
#		v4l2-ctl --list-devices				Set cap = cv2.VideoCapture( x ) to /dev/videox
#		workon cv1				to exit cv1 environment → deactivate
#		python c1.py

#	To Do Improvements:



#	Atom Settings:
#	Settings, Editor:
#		Check Show Invisibles
#		Tab Type = hard



import RPi.GPIO as GPIO
import serial
import os, sys, time, threading, ftplib, serial

#from ftplib import FTP, error_perm

from tkinter import *
import tkinter.font


#USB_GPS  = '/dev/ttyUSB0'
USB_LoRa = '/dev/ttyUSB1'
#USB_GPS  = '/dev/ttyUSB1'
#USB_LoRa = '/dev/ttyUSB0'

#ser = serial.Serial( USB_LoRa, 115200)		#	Went global because needed to asynchronously
ser = serial.Serial( USB_LoRa, 115200, timeout=10)		#	Went global because needed to asynchronously
											#	access from other functions

GPIO.setmode( GPIO.BOARD )
GPIO.setup( 7, GPIO.OUT )

p = GPIO.PWM(7,50)
p.start(7.5)

#  Normalize
temp_min = 0
temp_max = 600
y = 0.0000

home = '/home/pi/Desktop/locate/video'
if not os.path.exists(home):
    os.makedirs(home)
os.chdir(home)

win = Tk()
win.title("IOT BEAR Security")
myFont = tkinter.font.Font( family = 'Helvetica', size = 20, weight = "bold" )

motion_detected = False
#motion_detection = False		#	Is motion_detection activated
detecting_motion = False
# motion_enabled
# motion_activated
# searching_motion
# actively_detecting_motion
alarm_set = False
alarm_triggered = False
RX = False
LoRa_RX = False

sensors = [1, 3]	# ids of sensors
sensors_status = [-1, -1, -1]


def enable_alarm():
	global alarm_set
	alarm_set = True
	alarm_Status_Label["text"] = 'Alarm Set'
	enable_alarm_Button['state'] = DISABLED
	disable_alarm_Button['state'] = NORMAL


def disable_alarm():
	global alarm_set
	global alarm_triggered
	global LoRa_RX
	alarm_set = False
	alarm_triggered = False
	LoRa_RX = False
	alarm_Status_Label["text"] = 'Alarm Not Set'
	enable_alarm_Button['state'] = NORMAL
	disable_alarm_Button['state'] = DISABLED
	#win.disable_alarm_Button.config( state = "DISABLED" )


def door0():
	global alarm_set
	# global alarm_triggered
	#
	# if alarm_set == True:
	# 	alarm_triggered = True
	#
	# 	alarm_Status_Label["text"] = 'Alarm Triggered !'
	# 	disable_alarm_Button['state'] = NORMAL
	#
	# 	if LoRa_RX == True:
	# 		reply( "Alarm triggered !" )



def close():
	#RPi.GPIO.cleanup()
	win.destroy()


def setup_LoRa():
	#print ( serial.__version__ )
	global ser
	ser.write(b'AT+ADDRESS=9\r\n')
	time.sleep( 1 )
	ok = str(ser.readline())[2:-5]
	print(ok)



def goLoRa_RX0():
	global LoRa_RX
	LoRa_RX = not LoRa_RX
	if LoRa_RX == True:
		LoRa_RX_Button["text"] = 'LoRa RX Connected'
		t = threading.Thread( target = goLoRa_RX )
		t.daemon = True
		t.start()
	else:
		LoRa_RX_Button["text"] = 'LoRa RX'


def goLoRa_RX():
	print( "LoRa_RX" )
	global LoRa_RX
	global ser					#	So trigger can access this variable
								#	Requiring manual initializing to
								#	maintain modularity
	#ser = serial.Serial('/dev/ttyUSB0', 115200)
	#ser = serial.Serial(USB_LoRa, 115200)

	ser.write(b'AT+ADDRESS=2\r\n')
	time.sleep( 1 )

	while ( LoRa_RX == True ):
		#time.sleep( 1 )
		# Get rid of some of the junk at front and back
		#line = str(ser.readline())[2:-5]

		line = str( ser.readline().decode("utf-8") )
		print(line)

		#if "530" not in line:	#	Exception 530 Login authentication failed
		#	print(line)

		a = line.split(',')
		if len( a ) > 4:
			#print( len(  a[2] ) )
			LoRa_RX_Label["text"] = a[2]

	LoRa_RX_Button["text"] = 'LoRa RX'


def send_LoRa_TX( id, message ):
	global ser
	i = len( message )
	s = 'AT+SEND=' + str(id) + ',' + str( i ) + ',' + message + '\r\n'
	b = bytes( s, 'utf-8' )
	print ( "LoRa TX: {}".format( s ) )
	ser.write( b )
	ok = str(ser.readline())[2:-5]
	print(ok)


def LoRa_RX_timeout():
	# global ser

#	Method 1: ( No timeout )
 # in_waiting
 #    Getter:	Get the number of bytes in the input buffer
 #    Type:	int
 #
 #    Return the number of bytes in the receive buffer.
	#while ser.in_waiting:
#		print ( ser.readline() )

#	Method 2: ( timeout for 5 seconds )
	line = str( ser.readline().decode("utf-8") )
	print('LoRa RX: {}'.format( line ) )
	return line


def populate(line):
	if len( line ) == 0:
		return

	a = line.split(",")
	if len( a ) > 4:
		i = int( a[0][-1]) - 1
		sensors_status[ i ] = a[2]


def judge():
	for s in sensors_status:
		if s == 'True':
			print( 'Alert Door Open !')


def patrol0():
	if patrol1.get() == 1:
		t = threading.Thread( target = patrol )
		t.daemon = True
		t.start()


def patrol():
	global alarm_set
	global sensors
	#setup_LoRa()
	i = 0

	while patrol1.get() == 1:
		printStatus()
		send_LoRa_TX( sensors[i % len(sensors) ], "Testing!" )
		s = LoRa_RX_timeout()
		populate( s )
		if alarm_set == True:
			judge()
		i += 1
		time.sleep(10)


def printStatus():
	for s in sensors_status:
		print(' {}'.format(s), end='')
	print()


trigger_door_Button = Button(win, text = 'Trigger Door', command = door0, bg = 'bisque2', font = myFont )
trigger_door_Button.grid( row = 4, column = 1 )

#gps_coordinates = StringVar()
#gps_coordinates_Label = Label(win, text = '?', font = myFont, textvariable=gps_coordinates )
#gps_coordinates_Label = Label(win, text = '?', font = myFont )
#gps_coordinates_Label.grid( row = 5, column = 2 )

LoRa_RX_Button = Button(win, text = 'LoRa RX', command = goLoRa_RX0, bg = 'bisque2', font = myFont )
LoRa_RX_Button.grid( row = 7, column = 1 )

LoRa_RX_v = StringVar()		# Not using
#LoRa_RX_Label = Label(win, font = myFont, textvariable=LoRa_RX_v )
LoRa_RX_Label = Label(win, font = myFont )
LoRa_RX_Label.grid( row = 7, column = 2 )


#LoRa_TX_Button = Button(win, text = 'LoRa TX', command = send_LoRa_TX, bg = 'bisque2', font = myFont )
LoRa_TX_Button = Button(win, text = 'LoRa TX', command = lambda: send_LoRa_TX( 1, LoRa_TX_Entry.get() ), bg = 'bisque2', font = myFont )
LoRa_TX_Button.grid( row = 8, column = 1 )
tx_LoRa = StringVar()
LoRa_TX_Entry = Entry(win, font = myFont, textvariable=tx_LoRa )
LoRa_TX_Entry.grid( row = 8, column = 2 )

enable_alarm_Button = Button(win, text = 'Enable Alarm', state = NORMAL, command = enable_alarm, bg = 'bisque2', font = myFont )
enable_alarm_Button.grid( row = 9, column = 1 )

disable_alarm_Button = Button(win, text = 'Disable Alarm', state = DISABLED, command = disable_alarm, bg = 'bisque2', font = myFont )
disable_alarm_Button.grid( row = 10, column = 1 )

alarm_Status_Label = Label(win, text = 'Alarm Not Set', font = myFont )
alarm_Status_Label.grid( row = 10, column = 2 )


patrol1 = IntVar()
#Checkbutton(win, text="Patrol", variable=patrol1, command=patrol0, bg = 'bisque2', font=myFont ).grid(row=11, sticky=W)
Checkbutton(win, text="Patrol", variable=patrol1, command=patrol0, bg = 'bisque2', font=myFont ).grid(row=11, column = 1)


win.mainloop()
