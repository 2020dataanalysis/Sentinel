#	No TKinter
#	No GPIO

import time, threading, serial

#USB_LoRa = '/dev/ttyUSB0'
USB_LoRa = '/dev/ttyUSB1'
#ser = serial.Serial( USB_LoRa, 115200)					#	Went global because needed to asynchronously
ser = serial.Serial( USB_LoRa, 115200, timeout=10)		#	Went global because needed to asynchronously
														#	access from other functions
motion_detected = False
detecting_motion = False
alarm_set = False
alarm_triggered = False
RX = False
LoRa_RX = False
sensors = [1, 3]	# ids of sensors
sensors_status = [-1, -1, -1]

def enable_alarm():
	global alarm_set
	alarm_set = True
	#alarm_Status_Label["text"] = 'Alarm Set'
	#enable_alarm_Button['state'] = DISABLED
	#disable_alarm_Button['state'] = NORMAL


def disable_alarm():
	global alarm_set
	global alarm_triggered
	global LoRa_RX
	alarm_set = False
	alarm_triggered = False
	LoRa_RX = False
	#alarm_Status_Label["text"] = 'Alarm Not Set'
	#enable_alarm_Button['state'] = NORMAL
	#disable_alarm_Button['state'] = DISABLED
	#win.disable_alarm_Button.config( state = "DISABLED" )


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
		send_LoRa_TX( sensors[i % len(sensors) ], "Testing!" )
		s = LoRa_RX_timeout()
		populate( s )
		printStatus()
		if alarm_set == True:
			judge()
		i += 1
		time.sleep(10)


def printStatus():
	for s in sensors_status:
		print(' {}'.format(s), end='')
	print()
