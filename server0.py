#	11/19/2020		PIR Trigger
#	11/23/2020		FTP snapshots & filter by day.


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from security.setup import recipients_su, server_email_address, server_email_password
from security.credentials import users, recipients, arm_period, confirmation
import os
import time, threading
import serial
import datetime
import requests
import urllib
import shutil

import RPi.GPIO as GPIO											#	10/28/2020
GPIO.setmode(GPIO.BCM)											#	10/28/2020
green_led	= 26
red_led		= 27
GPIO.setup( green_led,	GPIO.OUT)
GPIO.setup( red_led, 	GPIO.OUT)


PIR_sensor = 17														#	10/28/2020
# sensor = 18														#	10/28/2020
# GPIO.setup(PIR_sensor, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)		#	10/28/2020		# Disables 04/24/2021 for bluetooth panasonic pir

from BLE_proximity import BLE_proximity
ble = BLE_proximity()
BLE_notification = False

import ftp_snapshot

#	Leaving LoRa as an option for possible future use.
USB_LoRa = '/dev/ttyUSB0'
#USB_LoRa = '/dev/ttyUSB1'
ser = serial.Serial( USB_LoRa, 115200, timeout=1)		#	Went global because needed to asynchronously
														#	access from other functions
alarm_set = True			#	Requires VIP to disarm.
alarm_set_session = False
alarm_trigger_count = 0
alarm_trigger_count_session = 0
trigger_time = 0
trigger_time_session = 0
alarm_triggered = False
alarm_triggered_session = False
door_triggered = 0
pir_trigger_time = 0
patrol = False
LoRa_RX = False
sensors = [1]
sensors_status = [-1, -1, -1]
sessioncount = 0
doorToggleCount = 0
door_open_count = 0									#	11/13/2020
response_log = []
response_count = 0
response_count_session = 0
start_time_revised = []
end_time_revised = []	#	Changed on security site.
time_revised = False			# 09/26/2020
VIP_first_log_in = False
token_user	= 'VIP'
token_password = '2021_Happy_Valentines'
PIR_false_trigger_second = -1
active_snapshots = False
active_snapshots_time = 0





#	================================================================
#	==========================	BLUETOOTH	========================
#	================================================================
# List process ID's that are using rfcomm:
	# sudo fuser /dev/rfcomm0
	# sudo lsof /dev/rfcomm0
	# sudo fuser -k /dev/rfcomm0		-k → to kill

# import threading, bluetooth, time, datetime, serial
import bluetooth
t_bluetooth = None
motion_time = 0
lux			= 0


def start_bluetooth_thread( mac, channel ):
	global t_bluetooth
	print( f'process started: { datetime.datetime.now() }' )
	# t_bluetooth = threading.Thread( target = bluetooth.process )
	t_bluetooth = threading.Thread( target = bluetooth.process, args=( mac, channel, ) )
	t_bluetooth.daemon = True
	t_bluetooth.start()






#					Activates on East office → shop.
def active(pin):
	global pir_trigger_time
	global alarm_set
	global PIR_false_trigger_second
	global active_snapshots

	if active_snapshots:
		return

	if alarm_set:
		s = datetime.datetime.now().second
		# print( f'server: {s}')
		if PIR_false_trigger_second == -1:
			PIR_false_trigger_second = s
			# return

		x = abs( PIR_false_trigger_second - s )
		PIR_false_trigger_second = s
		if x > 1:
			# v = GPIO.input(pin)
			# print("1 pin %s's value is %s" % (pin, v ))			#	Some times value is 0 → no motion
			# if v:
			# 	now				= int( time.time() ) % 86400		# Seconds since midnight
			# 	pir_lapse_time	= now - pir_trigger_time
			# 	if pir_lapse_time > 10 and pir_lapse_time < 60:
			# 		trigger(1, 'Motion detected')
			#
			# 	pir_trigger_time = int( time.time() ) % 86400		# Seconds since midnight
			# 	log_event('In Office.')
			# 	snapshot()										# I want it to state why it is taking a snapshot first.


			v = GPIO.input(pin)
			# print("1 pin %s's value is %s" % (pin, v ))			#	Some times value is 0 → no motion
			if v:
				PIR_false_trigger_second = -1
				log_event('In Office.')
				# trigger(1, 'Motion detected')					#	trigger( trigger type, message )
				snapshot(1)										# I want it to state why it is taking a snapshot first.



def alarmSchedule():
	#	Precursor	→	No VIP on site.
	#	This could be run once a minute if no input from user.
	global alarm_set
	global start_time
	global end_time
	global start_time_revised
	global   end_time_revised
	global response_log
	global time_revised
	global VIP_first_log_in
	global alarm_trigger_count			#	1/1/2021
	global alarm_triggered				#	1/2/2021
	global active_snapshots

	week = ['Monday', 'Teusday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	d = datetime.datetime.today().weekday()
	h = datetime.datetime.now().hour
	m = datetime.datetime.now().minute
	s = datetime.datetime.now().second
	hm = [h, m]

	if hm[0] == 0 and hm[1] < 1:
		# response_log = []			# Reset response log for the new day.
		# start_time_revised = []
		# end_time_revised = []

		# time_revised = False
		# VIP_first_log_in = False
		# alarm_trigger_count = 0
		# alarm_triggered = False
		resetAlarm()
		active_snapshots = False			#	For some reason door snaps stops working & stays not working.

	start_time	= ( toListTime( arm_period[week[d]][0]),	start_time_revised )[ bool( start_time_revised )]
	end_time	= ( toListTime( arm_period[week[d]][1]),	end_time_revised   )[ bool( end_time_revised   )]
	# print( '{} {},   now={} :{}'.format(start_time, end_time, hm, s ))

	if start_time <= hm and end_time > hm:
		#	Working hours
		if time_revised:
			# alarm_set = False
			# alarm_trigger_count = 0			#	11/25/2020
			# alarm_triggered = False
			resetAlarm()		#	This could cause a problem with VIP_first_log_in ??????????????????????????????????????????

	else:
		if not alarm_set:
			alarm_set = not alarm_set
			# print		( 'Scheduled Alarm Activation: alarm_set = {}'.format( alarm_set ))
			log_event	('Scheduled Alarm Activation: alarm_set = {}'.format( alarm_set ))


def resetAlarm():
	global alarm_set
	# global response_log
	global VIP_first_log_in
	global alarm_trigger_count			#	1/1/2021
	global alarm_triggered				#	1/2/2021

	time_revised = False
	VIP_first_log_in = False
	alarm_trigger_count = 0
	alarm_triggered = False
	alarm_set = False


def toDecimalTime( time ):
	h, m = map(int, time.split(':'))
	return ( h, h + float(m) / 60 )[ bool( m )  ]


def toListTime( time ):
	h, m = map(int, time.split(':'))
	return [h, m]


def add_recipients():
	week = ['Monday', 'Teusday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	d = datetime.datetime.today().weekday()
	h = datetime.datetime.now().hour
	m = datetime.datetime.now().minute
	s = datetime.datetime.now().second
	hm = [h, m]
	recipients_add = []

	# Triggers for the week
	if d < 5:
		if h >= 5 and h < 9:
			keith = '2020supersam@gmail.com'
			recipients_add.append( keith )
			rich = '5103777652@messaging.sprintpcs.com'
			recipients_add.append( rich )

		if h > 19 and h <= 22:
			keith = '2020supersam@gmail.com'
			recipients_add.append( keith )
			michael = '5104272873@vtext.com'
			recipients_add.append( michael )
	else:
		if h >= 6 and h <= 22:
			keith = '2020supersam@gmail.com'
			recipients_add.append( keith )
			michael = '5104272873@vtext.com'
			recipients_add.append( michael )

	recipients_add = []
	return recipients_add


def notify(type, subject, body):
	print('notify')
	recipients2 = []
	if type == 0:
		recipients2 = add_recipients()

	msg = MIMEMultipart()
	msg['From'] = server_email_address
	msg['To'] =  ", ".join( recipients )
	msg['To'] =  ", ".join( recipients2 )
	print('body = {}'.format( body ))
	msg['Subject'] = subject
	msg.attach(MIMEText(body, 'plain'))
	text = msg.as_string()
	email_server = smtplib.SMTP('smtp.gmail.com', 587)
	email_server.starttls()
	email_server.login(server_email_address, server_email_password)
	email_server.sendmail(server_email_address, recipients, text)
	email_server.quit()

































































































































def background_scheduler():
	#	Works outside of Flask so lazy loading may not work.
	#	Does not communicate with or rely on a session.
	#	This background scheduler executes with out the need of a client connection
	#	A database should be utilized because as of now session data is limited.
	#	In othe words, This thread should be the base of all data, the engine.
	global VIP_IN_dictionary
	global alarm_set
	global alarm_triggered
	global pir_trigger_time
	global PIR_sensor
	global VIP_first_log_in
	global BLE_notification
	global ble
	global alarm_trigger_count
	global time_revised
	global active_snapshots					#	Possibly temporary
	global active_snapshots_time
	global t_bluetooth

	setup_os()
	# GPIO.add_event_detect(PIR_sensor, GPIO.RISING, callback=active, bouncetime=100)
	GPIO.output( red_led, GPIO.LOW)
	GPIO.output( green_led, GPIO.LOW)

	count = 0
	#body = 'The alarm status can also be viewed at:\nAccess from local (BEAR) WiFi:	10.1.10.149:5000/security\nAccess from Remote:			96.86.182.158:5000/security\n'
	#notify( 'Door Test - security', body)
	# time.sleep( 1 )		#	Not sure if this is needed.
	alarmSchedule()		#	Because s < 3
	# print( f't_bluetooth.is_alive() = { t_bluetooth.is_alive() }' )

	while True:
		s = datetime.datetime.now().second
		# print( f'server: {s}')	# if s > 3:						#	Attempt to speed cycle time
		if s < 3 or time_revised:
			alarmSchedule()

		GPIO.output( green_led, GPIO.LOW)
		if ble.VIP_IN_dictionary:
			# GPIO.output( red_led, GPIO.LOW)		#  Will go off any ways in 2 seconds
			GPIO.output( green_led, GPIO.HIGH)
			if alarm_set:
				# alarm_set		= False
				# alarm_triggered = False
				# alarm_trigger_count = 0
				resetAlarm()
				log_event('VIP is in → Alarm deactivated.')

		# else:
		# 	alarmSchedule()

		patrol()

		# #	If motion is detected in the last 15 seconds
		# #	then do not check on doors.
		# now = int( time.time() ) % 86400		# Seconds since midnight
		# pir_lapse_time = now - pir_trigger_time
		# if pir_lapse_time > 15:					# Great for most cases except if person holds door open.
		# 										# Extend to 60 seconds or don't trigger unless door has been closed.
		# 										# May leave door open because will lock behind them.
		# 	if alarm_set:						# This can be moved to only check if vip is not in.
		# 		door_status()
		new_names = ble.VIP_BLE_added()
		for name in new_names:
			BLE_notification = True
			log_event(f'{name} is in.')


		# if ( new_names and alarm_set ):
		# 	# alarm_set = False
		# 	log_event('VIP is in → Alarm deactivated.')

			# if not VIP_first_log_in:								#	If you want to notify VIP once the log in.
			# 	VIP_first_log_in = True
			# 	p = '?user=' + token_user + '&password=' + token_password
				#body = 'The alarm status can also be viewed at:\nAccess from local (BEAR) WiFi:	10.1.10.149:5000/security' + p + '\nAccess from Remote:			96.86.182.158:5000/security' + p + '\n'
				#body = 'Access Alarm settings:\nLocal (BEAR) WiFi:	http://10.1.10.149:5000/security' + p + '\nRemote (Not using WiFi):			http://96.86.182.158:5000/security' + p + '\n'
				#body = '\nhttp://10.1.10.149:5000/security' + p + '\n\nhttp://96.86.182.158:5000/security' + p + '\n'
				#notify( 'Sentinel - Set Time', body)

		if s < 3:
			# alarmSchedule()

			name = ble.VIP_BLE_removed()
			if name:
				BLE_notification = True
				log_event(f'{name} is out.')

		#	Test for after hours movement
		GPIO.output( red_led, GPIO.LOW)
		if alarm_set:
			GPIO.output( red_led, GPIO.HIGH)
			if not alarm_triggered:
				door_status()

			# v = GPIO.input(PIR_sensor)
			# if v:
			# 	h = datetime.datetime.now().hour
			# 	m = datetime.datetime.now().minute
			# 	# if h > 8 and h < 18:
			# 	# 	if pir_lapse_time > 15:					# Great for most cases except if person holds door open.
			#
			# 	print("285 -  pin %s's value is %s" % (PIR_sensor, v ))			#	Some times value is 0 → no motion
			# 	now				= int( time.time() ) % 86400		# Seconds since midnight
			# 	pir_lapse_time	= now - pir_trigger_time
			# 	if pir_lapse_time > 10 and pir_lapse_time < 60:
			# 		trigger(1, 'Motion detected')

		if active_snapshots_time:
			lapse = int(time.time()) - active_snapshots_time
			if lapse > 60:
				active_snapshots = False
				active_snapshots_time = 0
				print('Active Snapshots Lapse Time')
				notify( 3, 'Active Snapshots Lapse Time' , 'Time Exceeded' )

		# GPIO.output( red_led, GPIO.LOW)
		GPIO.output( green_led, GPIO.LOW)
		time.sleep(1)
		GPIO.output( red_led, GPIO.LOW)				#	Will not see Red led if low before 1 second sleep.


		if t_bluetooth.is_alive():
			blue()




def relog_event( timestamp, subject ):
	global response_log
	global response_count

	message = timestamp + "→ " + subject
	response_count += 1
	d = {'data': message, 'count': response_count }
	response_log.append( d )


def log_event( subject ):
	global response_log
	global response_count

	timestamp = str( datetime.datetime.now() )[:-7]
	message = timestamp + "→ " + subject
	# print( message )
	response_count += 1
	d = {'data': message, 'count': response_count }
	response_log.append( d )
	home = "/home/pi/Desktop/sentinel"
	os.chdir(home)
	logfile = "/home/pi/Desktop/sentinel/log.txt"
	f = open("log.txt","a+")
	f.write( message+'\r\n' )
	f.close()


def patrol():
	# global alarm_set
	# global sensors
	#setup_LoRa()
	# i = 0			#	This needs to iterate through all sensors

	# for sensor in sensors:
		#send_LoRa_TX( sensors[i % len(sensors) ], "Testing!" )
		# send_LoRa_TX( sensor, "Testing!" )   																09/21  No more polling
	s = LoRa_RX_timeout()
	#s = 'a,b,door_open=1'
	# print( f'[{s}]' )
	#print( len( s ))

	populate( s )
	# printStatus()


def printStatus():
	for s in sensors_status:
		print(' {}'.format(s), end='')
	print()


def setup_LoRa():
	#print ( serial.__version__ )
	global ser
	ser.write(b'AT+ADDRESS=9\r\n')
	time.sleep( 1 )
	ok = str(ser.readline())[2:-5]
	# print(ok)


def send_LoRa_TX( id, message ):
	global ser
	i = len( message )
	s = 'AT+SEND=' + str(id) + ',' + str( i ) + ',' + message + '\r\n'
	b = bytes( s, 'utf-8' )
	# print ( "LoRa TX: {}".format( s ) )
	ser.write( b )
	ok = str(ser.readline())[2:-5]
	# print(ok)


def LoRa_RX_timeout():
	# print( 'a: ', end='')
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
#	+RCV=1,11,door_open=2,-71,47
	# print('rx')
	line = str( ser.readline().decode("utf-8") )
	# print( line )
	# s = datetime.datetime.now().second
	# print( f'server: {s}')	# if s > 3:						#	Attempt to speed cycle time


	# if s < 3:
	# 	line = '+RCV=1,11,door_open=2,-71,47'

	if line:
		print('LoRa RX: {}'.format( line ) )
		if line[:4] == '+ERR':									# This error occurs about twice a month & will stop successful working.
			print( 'Error Report' )
			line = ''
			notify( 3, 'LoRa Communication Error' , 'The Raspberry Pi LoRa RX module received the message: +ERR' )

	# return '+RCV=1,11,door_open=2,-71,47'				#	Trigger Open Door
	return line


def populate(line):
	global doorToggleCount
	global sensors_status								#	09/22/2020
	global door_open_count

	state = "closed"									#	If not receiving open LoRa then assume it is closed.

	if len( line ) == 0:
		sensors_status[ 1 ] = "closed1"
		sensors_status[ 2 ] = "closed2"
		door_open_count = 0
		return

	# sensors_status[ 1 ] = "closed1"
	# sensors_status[ 2 ] = "closed2"
	# return
	a = line.split(",")
	# print( a )

	#i = int( a[0][-1]) - 1			# Used if multiple LoRa's, Front door is index = 0
	#sensors_status[ i ] = a[2]
	#print("a[2] = {}".format(a[2]))

	# if a[2][:] == 'door_open=1':					#			***********************************************  Temp fix.
	if a[2][:-1] == 'door_open=':
		state = "open"
		i = int( a[2][-1] )
		# print(f'i=[{i}]')
		subject = 'Door {} Opened'.format( i )
		# log_event( subject )
		s = state + str( i )
		if sensors_status[ i ] != s:		#	This can be eliminated ********************
			sensors_status[ i ] = s
			log_event( subject )			#	10/22/2020 → to eliminate repeat open signals.
			snapshot( 6 )


		#	This way requires reading next door open signal
		# door_open_count += 1
		# if door_open_count < 10:			#	Door may not properly close.
		# 	snapshot()


def setup_os():
	removeFiles( '/home/pi/motion' )

	home = "/home/pi/Desktop/sentinel"
	os.chdir(home)

	logfile = "/home/pi/Desktop/sentinel/log.txt"
	if os.path.isfile( logfile ):
		f = open("log.txt", "r")
		fl = f.readlines()
		for x in fl:
			# print (x)
			a = x.split('→')
			relog_event( a[0], a[1].strip() )			#	Strip the left space & right carriage return

		f.close()

	initBlueTooth()


def initBlueTooth():
	global t_bluetooth
	global bluetoothSerial


	doors = '80:7D:3A:DC:C6:42'
	channel = '1'

	# PIR = '84:0D:8E:21:06:7E'
	channel = '2'

	start_bluetooth_thread( doors, channel )
	# start_bluetooth_thread( PIR, channel )
	time.sleep( 1 )
	bluetoothSerial = None

	while not bluetoothSerial:
		if not t_bluetooth.is_alive():
			start_bluetooth_thread( PIR, channel )
		time.sleep( 1 )

		if t_bluetooth.is_alive():
			bluetoothSerial	= serial.Serial("/dev/rfcomm0", baudrate=115200, timeout=0 )
		else:
			t = 10
			print(f'Retrying in {t} seconds.')
			time.sleep( t )

	print(f'bluetoothSerial = {bluetoothSerial}')




# def blue0():
# 	global t_bluetooth
#
# 	while t_bluetooth.is_alive():
# 		blue()
# 		time.sleep( 1 )




def blue():
	global alarm_set
	global t_bluetooth
	global bluetoothSerial
	global motion_time
	global lux

	import time

	try:
		# print("1")
		if t_bluetooth.is_alive():
			# print("2")
			s	= bluetoothSerial.readline().decode("utf-8")
			# hex_string = binascii.hexlify(s).decode('utf-8')

			# if s:
			while s:
				# print ( len( s ))
				# print( f'[{s}]', end='' )
				# print( f'{s}', end='' )
                # print( f'process started: { datetime.datetime.now() }'
				a = s.split('=')

				if a[0] == 'motion':
					t = datetime.datetime.now()
					print( f'{ t }: Motion: { a[0] } → { a[1] }' )
					# if a[1] == '1':
					value = int( a[1].strip() )
					# print(f'[{a[1]}]')
					if value == 1:
						now = int( time.time() ) % 86400		# Seconds since midnight
						lapse = now - motion_time
						if lapse > 60:
							motion_time = now
							log_event('Panasonic - In Office.')
							# trigger(1, 'Motion detected')					#	trigger( trigger type, message )
							snapshot(5)										# I want it to state why it is taking a snapshot first.

							if alarm_set:
								trigger(1, 'Alarm Triggered ! - Panasonic PIR.' )

						else:
							print( f'{ t }: Skip Panasonic Motion: { a[0] } → { a[1] }' )		#	1 event can trigger 3 messages → last message should be a skip.
					# s	= bluetoothSerial.readline().decode("utf-8")


				if a[0] == 'light':
					print( f'{ datetime.datetime.now() }: Light: { a[0] } → { a[1] }' )
					now_lux = int( a[1].strip() )
					dif_lux = abs( now_lux - lux )
					if dif_lux > 70:
						lux = now_lux
						log_event( f'Office Light - LUX = { lux }')
						# trigger(1, 'Motion detected')					#	trigger( trigger type, message )
						snapshot(1)										# I want it to state why it is taking a snapshot first.
						if alarm_set & lux > 100:
							trigger(1, 'Alarm Triggered ! - Office lights are turned on.' )

				s	= bluetoothSerial.readline().decode("utf-8")



	except serial.SerialException as e:
		if e.errno == 2:
			# raise e
			print( f'Error {e.errno}: Serial bluetooth is not connected. ')


	except KeyboardInterrupt:
		print("Quit")







	# #	If here then assume alarm is set.
	# global alarm_triggered
	# global alarm_trigger_count
	# global trigger_time
	# global door_triggered
	# global sensors_status										# 9/22/2020
	#
	# for s in sensors_status:
	# 	if isinstance(s, str) and 'open' in s:
	# 	#if isinstance(s, str) and 'close' in s:
	# 		#print( 'Alert Door Open !')
	# 		#socketio.emit('alarm_triggered', namespace='/test', broadcast=True)
	# 		alarm_triggered = True
	# 		#door_triggered = str( sensors_status.index( s ) + 1 )				# Door
	# 		print( f'sensors_status.index={sensors_status.index( s )}')
	# 		door_triggered = sensors_status.index( s )							#	0		Not Used																#	1		Index 1
	#
	# if alarm_triggered:
	# 	trigger(0, 'Alarm Triggered ! - Door ' + str( door_triggered ) + ' is open.' )











def removeFiles(path):
	os.chdir( path )
	for entry in os.scandir( path ):
		if entry.name.startswith('.'):
			continue
		# if entry.name.endswith('.mkv'):			#	Should not need to remove.  Set motion.conf to high so it never creates a video file.
		# 	continue
		# print( 'removeFiles → ' + entry.name )
		os.remove( entry.name )					#	Deletes all .jpg files, so in snapshot
												#	the first .jpg is the last is the one i need.






































def snapshot( snaps ):
	global active_snapshots
	global active_snapshots_time

	if active_snapshots:
		print('active_snapshots')
		return

	active_snapshots_time = int( time.time() )
	active_snapshots = True
	#	Delete all, requests.get, the 1 remaining is the one you want.  & assign name.
	# image = ''
	removeFiles( '/home/pi/motion' )


	# snapshot_thread( snaps )
	# ftp_snapshot.ftp0()
	t1 = threading.Thread( target = snapshot_thread, args=(snaps,) )
	t1.daemon = True
	t1.start()
	t1.join()				#	This is needed for ftp_snapshot → os.remove()



def snapshot_thread( snaps ):
	global active_snapshots
	global active_snapshots_time

	for i in range( snaps ):
		requests.get('http://localhost:8080/0/action/snapshot')
		time.sleep( 1 )

	motion = '/home/pi/motion'
	snapshot_list = os.listdir( motion )
	ftp_snapshot.ftp()

	# time.sleep( 5 )
	log_snapshots( snapshot_list )

	time.sleep( snaps * 2)					#	1/15/2021		Thank you big help !
	active_snapshots_time = 0
	active_snapshots = False


def log_snapshots( snapshot_list ):
	for image in sorted( snapshot_list ):
		if image == 'lastsnap.jpg':
			continue

		if image.endswith('.jpg'):
			print( f'log_snapshots [{ image }]')
			log_event( image )


def door_status():
	#	If here then assume alarm is set.
	global alarm_triggered
	global alarm_trigger_count
	global trigger_time
	global door_triggered
	global sensors_status										# 9/22/2020

	for s in sensors_status:
		if isinstance(s, str) and 'open' in s:
		#if isinstance(s, str) and 'close' in s:
			#print( 'Alert Door Open !')
			#socketio.emit('alarm_triggered', namespace='/test', broadcast=True)
			alarm_triggered = True
			#door_triggered = str( sensors_status.index( s ) + 1 )				# Door
			print( f'sensors_status.index={sensors_status.index( s )}')
			door_triggered = sensors_status.index( s )							#	0		Not Used																#	1		Index 1

	if alarm_triggered:
		trigger(0, 'Alarm Triggered ! - Door ' + str( door_triggered ) + ' is open.' )



#	The initial trigger sends emails & text messages.
#	With follow up emails in a quadratic delaying notification process.
#	99% of triggers are by human laziness.
#	This algorithm will be cancelled.
# def trigger(type, message ):
# 	global alarm_triggered
# 	global alarm_trigger_count
# 	global trigger_time
# 	global door_triggered
# 	global sensors_status										# 9/22/2020
#
# 	if alarm_trigger_count == 0:
# 		log_event( message  )
# 		trigger_time = int( time.time() ) % 86400		# Seconds since midnight
#
# 	else:						# 03/02/2021   Reset alarm trigger based on time.
# 		if alarm_trigger_count > 4:
# 			resetAlarm()
#
#
# 	wait_time = (2**alarm_trigger_count - 1) * 60
# 	# wait_time = 60	* 60			#	 1 hour, reset trigger after
# 	now = int( time.time() ) % 86400		# Seconds since midnight
#
# 	# print( '{} + {} = {} - {}'.format(trigger_time, wait_time, trigger_time + wait_time, now ))
# 	if trigger_time + wait_time <= now:
# 		alarm_trigger_count += 1
# 		#body = 'The alarm status can also be viewed at:\nAccess from local (BEAR) WiFi:	10.1.10.149:5000/security\nAccess from Remote:			96.86.182.158:5000/security\n'
# 		p = '?user=' + token_user + '&password=' + token_password
# 		# body = '\nhttp://10.1.10.149:5000/security' + p + '\n\nhttp://96.86.182.158:5000/security' + p + '\n'				#	Sent when trust use appropriately
# 		body = '\n\nhttp://96.86.182.158:5000/security' + p + '\n'				#	Sent when trust use appropriately
# 		# body = '\nhttp://10.1.10.149:5000' + '\n\nhttp://96.86.182.158:5000' + '\n'
#
# 		# This is too much for a text message
# 		# for i in response_log:
# 		# 	body += '#' + str( i['count'] ) + ': ' + i['data'] + '\n'
#
# 		notify( type, 'Alert ' + message, body )
#
# 		log_event( 'Alarm Trigger Notification ' + str( alarm_trigger_count ) + ' Sent !'  )



#	Since, 99% of triggers are by human laziness.
#	The initial trigger sends emails & text messages.
#	No follow up emails.
#	Trigger is reset to continue to allow more triggers.
def trigger(type, message ):
	global alarm_triggered
	global alarm_trigger_count
	global trigger_time
	global door_triggered
	global sensors_status										# 9/22/2020

	if alarm_trigger_count == 0:
		wait_time = 0
		log_event( message  )
		trigger_time = int( time.time() ) % 86400		# Seconds since midnight

	else:						# 03/02/2021   Reset alarm trigger based on time.
		wait_time = 60

	now = int( time.time() ) % 86400		# Seconds since midnight

	if trigger_time + wait_time <= now:
		trigger_time = int( time.time() ) % 86400		# Seconds since midnight
		# resetAlarm()
		alarm_trigger_count += 1
		p = '?user=' + token_user + '&password=' + token_password
		body = '\n\nhttp://96.86.182.158:5000/security' + p + '\n'				#	Sent when trust use appropriately

		notify( type, 'Alert ' + message, body )
		log_event( 'Alarm Trigger Notification ' + str( alarm_trigger_count ) + ' Sent !'  )














def emit_response( subject ):		#	First Log event → flags a change in the log		→	broadcast change
	global response_log
	global response_count

	log_event( subject )
	d = response_log[-1]
