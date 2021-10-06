#	IOT Security system supporting presence ID detection, email & text alerts, timestamp image log.  Raspberry Pi, multiple esp32 microcontrollers, cameras.  Flask, MQTT, BLE, ...
#	https://github.com/2020dataanalysis/Sentinel.git
#	Sam Portillo
#	10.05.2021


#	04/29/2021 		Bluetooth & Terminal
#	11/23/2020		FTP snapshots & filter by day.

import os, time, datetime, threading, smtplib, requests, urllib, shutil
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
from security.setup import recipients_su, server_email_address, server_email_password
from security.credentials import users, recipients, arm_period, confirmation

#	Plan to remove leds for Terminal
import RPi.GPIO as GPIO											#	10/28/2020
GPIO.setmode(GPIO.BCM)											#	10/28/2020
green_led	= 26
red_led		= 27
# GPIO.setup( green_led,	GPIO.OUT)
# GPIO.setup( red_led, 	GPIO.OUT)

PIR_sensor = 17														#	10/28/2020
# sensor = 18														#	10/28/2020
# GPIO.setup(PIR_sensor, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)		#	10/28/2020		# Disables 04/24/2021 for bluetooth panasonic pir


import json			#	06.21.2021

from BLE_proximity import BLE_proximity
ble = BLE_proximity()
BLE_notification = False

import ftp_snapshot

#	Leaving LoRa as an option for possible future use.
USB_LoRa = '/dev/ttyUSB0'
#USB_LoRa = '/dev/ttyUSB1'
# ser = serial.Serial( USB_LoRa, 115200, timeout=1)		#	Went global because needed to asynchronously
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
sensors_status = [-1, -1, -1]		##############################
sessioncount = 0
doorToggleCount = 0
door_open_count = 0									#	11/13/2020
response_log = []					################################
response_count = 0
response_count_session = 0
start_time_revised = []
end_time_revised = []	#	Changed on security site.
time_revised = False			# 09/26/2020
VIP_first_log_in = False
token_user	= 'VIP'
token_password = '4thJuly'
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
# import bluetooth
t_bluetooth = None
motion_time = 0
motion_time_TOF = 0
door_time 	= 0
lux			= 0

start_time = []		# 05/04/2021
end_time 	= []
VIP_IN_dictionary = {}			#	06/15/2021
VIP_IN = {}

from copy import deepcopy
from server_mqtt import MQTT
mqtt = MQTT('sentinelserver')
# mqtt.subscribe_list = [ 'office/door1', 'office/door2', 'office', 'office/sonic', 'office/pir', 'office/lux', 'shop', 'zigbee2mqtt/0x286d9700010d9cd0', 'zigbee2mqtt/Aqara', 'flask', 'online' ]
mqtt.subscribe_list = [ 'office/door1', 'office/door2', 'office', 'office/sonic', 'office/pir', 'office/lux', 'shop', 'zigbee2mqtt/Samsung', 'zigbee2mqtt/Aqara', 'flask', 'online', 'enforcer', 'enforcer/lux', 'TOF', 'TOF/pir', 'TOF/sonic' ]
mqtt.mqtt_subscribe()
location = mqtt.location

zigbee_door_contact = True
zigbee_aqara_door_contact = True

# import mysql.connector						#	06/13/2021

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

	# print('alarm_schedule')
	week = ['Monday', 'Teusday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	d = datetime.datetime.today().weekday()
	h = datetime.datetime.now().hour
	m = datetime.datetime.now().minute
	s = datetime.datetime.now().second
	hm = [h, m]

	if hm[0] == 0 and hm[1] < 1:
		resetAlarm()
		active_snapshots = False			#	For some reason door snaps stops working & stays not working.

	start_time	= ( toListTime( arm_period[week[d]][0]),	start_time_revised )[ bool( start_time_revised )]
	end_time	= ( toListTime( arm_period[week[d]][1]),	end_time_revised   )[ bool( end_time_revised   )]
	# print( '{} {},   now={} :{}'.format(start_time, end_time, hm, s ))

	if start_time <= hm and end_time > hm:
		#	Working hours
		if time_revised:
			resetAlarm()

	else:
		if not alarm_set:
			alarm_set = not alarm_set
			# print		( 'Scheduled Alarm Activation: alarm_set = {}'.format( alarm_set ))
			log_event	('Scheduled Alarm Activation: alarm_set = {}'.format( alarm_set ))
			publish_command_mqtt( 'command/office/doors/terminal', 'print=0,0,5,0,Alarm Set' )


def resetAlarm():
	global alarm_set
	global VIP_first_log_in
	global alarm_trigger_count			#	1/1/2021
	global alarm_triggered				#	1/2/2021
	global time_revised					#   4/29/2021

	time_revised = False
	VIP_first_log_in = False
	alarm_trigger_count = 0
	alarm_triggered = False
	alarm_set = False
	publish_command_mqtt( 'command/office/doors/terminal', 'print=0,0,4,0,Alarm Not Set' )


def refresh_display():
	global alarm_set

	if alarm_set:
		publish_command_mqtt( 'command/office/doors/terminal', 'print=0,0,5,0,Alarm Set' )
	else:
		publish_command_mqtt( 'command/office/doors/terminal', 'print=0,0,4,0,Alarm Not Set' )



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


def get_date():
	from datetime import date
	todays_date = date.today()
	print("Current date: ", todays_date)

	# fetching the current year, month and day of today
	# print("Current year:", todays_date.year)
	# print("Current month:", todays_date.month)
	# print("Current day:", todays_date.day)
	return [ todays_date.year, todays_date.month, todays_date.day ]


def get_time():
	h = datetime.datetime.now().hour
	m = datetime.datetime.now().minute
	s = datetime.datetime.now().second
	return [h, m, s]


def notify(type, subject, body):
	from email.mime.text import MIMEText
	from email.mime.multipart import MIMEMultipart

	print('notify')
	recipients2 = []
	if type == 0:
		recipients2 = add_recipients()

	msg = MIMEMultipart()
	msg['From'] = server_email_address
	msg['To'] =  ", ".join( recipients )
	msg['To'] =  ", ".join( recipients2 )
	# print('body = {}'.format( body ))
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
	global VIP_IN
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
	# global client
	global sensors_status
	global mqtt

	setup_os()
	# GPIO.add_event_detect(PIR_sensor, GPIO.RISING, callback=active, bouncetime=100)
	# GPIO.output( red_led, GPIO.LOW)
	# GPIO.output( green_led, GPIO.LOW)

	count = 0
	alarmSchedule()		#	Because s < 3

	# client.publish( 'command/door', payload='status', qos=0, retain=True )
	# client.loop(1)		#blocks for 1000ms

	notify( 3, 'Start' , 'Test email' )

	while True:
		s = datetime.datetime.now().second
		# print( f'server: {s}')	# if s > 3:						#	Attempt to speed cycle time

		VIP_IN_dictionary = ble.VIP_IN_dictionary		#	06/16/2021
		# VIP_IN[] = VIP_IN_dictionary[name] = self.t

		# print( f'457 server: { VIP_IN }' )
		if ble.VIP_IN_dictionary:
			if alarm_set:
				resetAlarm()
				log_event('VIP is in → Alarm deactivated.')

		else:
			if s < 3 or time_revised:
				alarmSchedule()

		# MQTT triggers → do not need to poll
		# patrol()

		new_names = ble.VIP_BLE_added()
		if new_names:
			for name in new_names:
				BLE_notification = True
				log_event(f'{name} is in.')

		if s < 3:
			name = ble.VIP_BLE_removed()
			if name:
				BLE_notification = True
				log_event(f'{name} is out.')

		if alarm_set:
			# if not alarm_triggered:
			door_status()

		if active_snapshots_time:
			lapse = int(time.time()) - active_snapshots_time
			if lapse > 80:
				active_snapshots = False
				active_snapshots_time = 0
				print('478 Active Snapshots Lapse Time')
				notify( 3, 'Active Snapshots Lapse Time' , 'Time Exceeded' )

		if not mqtt.mqtt_online_test():
			notify( 3, 'Online Lapse Time' , 'Time Exceeded > 90' )

		mqtt_check_messages()

		time.sleep( 1 )



def mqtt_check_messages():
	global mqtt

	s = datetime.datetime.now().second
	messages_race = deepcopy( mqtt.messages )
	for i in messages_race.items():
		print( f'{s} { i[0] } { i[1] }' )
		messages( i[0], i[1] )


	mqtt.messages = {}			# May lose changes while iterating but avoiding a race condition.





def publish_mqtt_events():
	global location
	global alarm_set
	global start_time
	global end_time
	global VIP_IN_dictionary
	global response_log
	global sensors_status
	global mqtt

	# print( f'alarm_set → {alarm_set}')
	# print( f'VIP_IN → {VIP_IN_dictionary}')
	# print( f'response_log → {response_log}')
	print('publish_mqtt_events...', end='')
	publish_command_mqtt( 'location', mqtt.location )
	publish_command_mqtt( 'alarm_set', alarm_set )
	publish_command_mqtt( 'alarm_set', alarm_set )
	publish_command_mqtt( 'start_time', json.dumps( start_time ) )
	publish_command_mqtt( 'end_time', json.dumps( end_time ) )
	publish_command_mqtt( 'response_log', json.dumps( response_log ) )
	publish_command_mqtt( 'VIP_IN', json.dumps( VIP_IN_dictionary ) )
	publish_command_mqtt( 'sensors_status', json.dumps( sensors_status ))
	print('done.')


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
	print( message )
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
	print('patrol')


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






def populate( door, status ):
	global doorToggleCount
	global sensors_status								#	09/22/2020
	global door_open_count
	global door_time
	# global alarm_triggered

	print( 'populate' )
	if sensors_status[ door ] != status:		#	This can be eliminated ********************
		# print( sensors_status )
		sensors_status[ door ] = status
		# print( sensors_status )
		if status:
			subject = 'Door {} is open'.format( door )
			log_event( subject )
			snapshot( 1, 6 )			#	1 → camera 1
		else:
			subject = 'Door {} is closed'.format( door )
			log_event( subject )
			refresh_display()					#	mqtt 06/30/2021


def setup_os():
	# global mqtt

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

	# initBlueTooth()
	# mqtt.mqtt_subscribe()
	# db()



def initBlueTooth():
	global t_bluetooth
	global bluetoothSerial

	doors = '80:7D:3A:DC:C6:42'
	channel = '1'

	# PIR = '84:0D:8E:21:06:7E'
	# channel = '2'

	start_bluetooth_thread( doors, channel )
	# start_bluetooth_thread( PIR, channel )
	time.sleep( 1 )
	bluetoothSerial = None

	while not bluetoothSerial:
		if not t_bluetooth.is_alive():
			start_bluetooth_thread( doors, channel )
		time.sleep( 1 )

		if t_bluetooth.is_alive():
			bluetoothSerial	= serial.Serial("/dev/rfcomm0", baudrate=115200, timeout=0 )
		else:
			t = 10
			print(f'Retrying in {t} seconds.')
			time.sleep( t )

	print(f'bluetoothSerial = {bluetoothSerial}')


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


def snapshot( camera, snaps ):
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
	t1 = threading.Thread( target = snapshot_thread, args=(camera, snaps,) )
	# t1.daemon = True					# Disabled 07/05/2021
	t1.start()
	t1.join()				#	05/25/2021			#	This is needed for ftp_snapshot → os.remove()

	#	****************************************************************************************


def snapshot_thread( camera, snaps ):
	# print('snapshot_thread ************')
	global active_snapshots
	global active_snapshots_time
	global location			#	05.26.2021

	for i in range( snaps ):

		if camera == 1:
			requests.get('http://localhost:8080/0/action/snapshot')

		if camera == 2:
			curl( 'http://admin:@10.0.0.190/image.jpg' )

		if camera == 3:
			# requests.get('http://localhost:8080/0/action/snapshot')
			size = 0
			while size < 100000:
				# if size < 100000:
				removeFiles( '/home/pi/motion' )
				# size = curl( 'http://10.0.0.64/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUCeI9WG7C&user=admin&password=' )
				size = curl( 'http://10.0.0.109/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUCeI9WG7C&user=admin&password=' )
				# print('Recurl')
				time.sleep( 1 )
				# curl( 'http://10.0.0.64/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUCeI9WG7C&user=admin&password=' )

		time.sleep( 1 )

	motion = '/home/pi/motion'
	snapshot_list = os.listdir( motion )
	ftp_snapshot.ftp( location )

	log_snapshots( snapshot_list )

	time.sleep( snaps * 3 )					#	1/15/2021		Thank you big help !
	active_snapshots_time = 0
	active_snapshots = False


def curl( url ):
	import subprocess

	date = get_date()
	time = get_time()

	name = f'image_{ date[0] }-{ date[1] }-{ date[2] }_{ time[0] }:{ time[1] }:{ time[2] }.jpg'
	print( name )
	# name = 'cool' + str( i ) + '.jpg'
	process = subprocess.Popen(['curl', url, '-o', name ],
	                     stdout=subprocess.PIPE,
	                     stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()
	print( stdout, stderr )

	return os.path.getsize( name )


def log_snapshots( snapshot_list ):
	for image in sorted( snapshot_list ):
		if image == 'lastsnap.jpg':
			continue

		if image.endswith('.jpg'):
			# print( f'log_snapshots [{ image }]')
			log_event( image )


def door_status():
	#	If here then assume alarm is set.
	global alarm_triggered
	global alarm_trigger_count
	global trigger_time
	global door_triggered
	global sensors_status										# 9/22/2020


	if not alarm_triggered:
		if 1 in sensors_status:
			alarm_triggered = True
			door_triggered = sensors_status.index( 1 )
			trigger(0, 'Alarm Triggered ! - Door ' + str( door_triggered ) + ' is open.' )

	else:
	# if alarm_triggered:
		if 1 not in sensors_status:
			alarm_triggered = False
			# trigger(0, 'Alarm Triggered ! - Door ' + str( door_triggered ) + ' is open.' )



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
	global location

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
		if location == 'blackhawk':
			body = '\n\nhttp://73.223.16.32:5000/security' + p + '\n'				#	Sent when trust use appropriately

		notify( type, 'Alert ' + message, body )
		log_event( 'Alarm Trigger Notification ' + str( alarm_trigger_count ) + ' Sent !'  )


def emit_response( subject ):		#	First Log event → flags a change in the log		→	broadcast change
	global response_log
	global response_count

	log_event( subject )
	d = response_log[-1]



def messages( topic, payload ):
	global zigbee_door_contact
	global zigbee_aqara_door_contact
	global motion_time
	global motion_time_TOF
	global lux

	t = datetime.datetime.now()
	print( f'{ t } - { topic } → { payload }' )

	if topic == 'flask':
		publish_mqtt_events()
		return

	if topic == 'online':
		mqtt.mqtt_online_test_result()
		return


	# if topic == 'zigbee2mqtt/0x286d9700010d9cd0':
	if topic == 'zigbee2mqtt/Samsung':
		false = False
		true = True
		d = eval( payload )
		# print( d )

		f = d['temperature'] * 9 / 5 + 32
		contact = d['contact']
		print( f'Fahrenheit : {f}' )
		print( f'contact : { contact }' )
		# populate( door_number, door_status )

		if zigbee_door_contact != contact:
			zigbee_door_contact = contact

			if contact :
				log_event( f'Zigbee Door is closed. {f}°')
				snapshot(1, 1)

			if not contact:
				log_event( f'Zigbee Door is open. {f}°')
				snapshot(1, 1)

		return


	# if topic == 'zigbee2mqtt/0x00158d0006f98451':
	if topic == 'zigbee2mqtt/Aqara':
		false = False
		true = True
		d = eval( payload )

		f = d['temperature'] * 9 / 5 + 32
		contact = d['contact']
		print( f'Fahrenheit : {f}' )
		print( f'contact : { contact }' )
		# populate( door_number, door_status )

		if zigbee_aqara_door_contact != contact:
			zigbee_aqara_door_contact = contact

			if contact :
				log_event( f'Zigbee Aqara Door is closed. {f}°')
				snapshot(1, 1)

			if not contact:
				log_event( f'Zigbee Aqara Door is open. {f}°')
				snapshot(1, 1)

		return


	value = int( payload )

	if topic == 'office/pir':
		if value > 0:
			now = int( time.time() ) % 86400		# Seconds since midnight
			lapse = now - motion_time
			if lapse < 0 or lapse > 10:			# < 0 when 86400 mod 86400 = 0  at midnight
				motion_time = now
				m = f'{ topic } = { value }'
				log_event( m )
				snapshot(1, 2)										# I want it to state why it is taking a snapshot first.
				print( m )

				if alarm_set:
					trigger( 1, f'Alarm Triggered ! - ' + m )

			else:
				print( f'{ t } { lapse }: Skip ' )



	if topic == 'TOF/sonic':
		if value > 0:
			now = int( time.time() ) % 86400		# Seconds since midnight
			lapse = now - motion_time_TOF
			if lapse < 0 or lapse > 10:			# < 0 when 86400 mod 86400 = 0  at midnight
				motion_time_TOF = now
				m = f'{ topic } = { value }'
				log_event( m )
				snapshot(1, 2)										# I want it to state why it is taking a snapshot first.
				print( m )

				if alarm_set:
					trigger( 1, f'Alarm Triggered ! - ' + m )

			else:
				print( f'{ t } { lapse }: Skip ' )






	if topic == 'enforcer':
		if value > 0:
			now = int( time.time() ) % 86400		# Seconds since midnight
			lapse = now - motion_time
			if lapse < 0 or lapse > 10:			# < 0 when 86400 mod 86400 = 0  at midnight
				motion_time = now
				m = f'{ topic } = { value }'
				log_event( m )
				snapshot(2, 2)										# I want it to state why it is taking a snapshot first.
				print( m )

				if alarm_set:
					trigger( 1, f'Alarm Triggered ! - ' + m )

			else:
				print( f'{ t } { lapse }: Skip ' )



	if topic == 'office/lux':
		dif_lux = abs( value - lux )

		if dif_lux > 10:
			if not lux:
				lux = 1

			lux_percent_change = dif_lux / lux
			if lux_percent_change > .1:
				lux = value
				log_event( f'{ topic } = { lux }' )
				# trigger(1, 'Motion detected')					#	trigger( trigger type, message )
				snapshot(2, 1)										# I want it to state why it is taking a snapshot first.
				if alarm_set & lux > 100:
					trigger( 1, 'Alarm Triggered ! - Office lights are turned on.' )


	# if topic == 'TOF/sonic':
	# 	log_event( f'{ topic } → { value }' )
	# 	snapshot(1, 1)										# I want it to state why it is taking a snapshot first.




	if topic == 'office/door1':
		door_number = 1
		door_status = value
		populate( door_number, door_status )


	if topic == 'office/door2':
		door_number = 2
		door_status = value
		populate( door_number, door_status )




def publish_command_mqtt( topic, payload ):
	global mqtt

	mqtt.publish_command( topic, payload )




def db():
	global cnx
	global cursor

	# import mysql.connector

	cnx = mysql.connector.connect(
	  host="localhost",
	  user="sam",
	  password="aszx",
	  database="sentinel"
	)

	cursor = cnx.cursor()
	cursor.execute("DELETE FROM status")
	cnx.commit()

	insert_sql  = ( "INSERT INTO status "
	                "(alarm_set, alarm_triggered, time_revised, start_time_revised, end_time_revised) "
	                "VALUES (%s, %s, %s, %s, %s)")

	insert_data = (False, False, False, 0, 0)

	cursor.execute( insert_sql, insert_data )
	cnx.commit()
	rc = cursor.rowcount
	print("%d"%rc)
	# e=cur.execute("DELETE FROM `acc_details` WHERE roll_No=%s" % roll)
	# print("%d"%cur.rowcount)


background_scheduler()
