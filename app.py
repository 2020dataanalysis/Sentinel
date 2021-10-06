#	Flask client
#	Displays log with timestamped images
#	Sam Portillo
#	10.05.2021

# flask run --host=0.0.0.0

import threading, logging, requests, urllib, datetime
from threading import Lock
from flask import Flask, render_template, session, request, copy_current_request_context
import paho.mqtt.client as mqtt
import time, datetime
import json

app = Flask(__name__)
thread = None
thread_lock = Lock()
# from route import *

location	= None
alarm_set			= False
start_time = [1, 0]
end_time = [20, 0]
VIP_IN = {}
sensors_status = []
response_log = []
online_lapse_time = int( time.time() )
client = None		# MQTT


from copy import deepcopy
from server_mqtt import MQTT
mqtt = MQTT('Flask')
mqtt.subscribe_list = [ 'location', 'alarm_set', 'VIP_IN', 'start_time', 'end_time', 'response_log', 'sensors_status', 'keepalive' ]
mqtt.mqtt_subscribe()
location = mqtt.location
# # from route import *


def get_days( temp_log ):
	# print('get_days')
	# print( len( server.response_log ))
	days_list = []

	for log in temp_log:
		data = log['data']
		# print( f'data= {data}')
		date = data.split(" ")[0]
		# print( f'day={date}' )
		days_list.append( date )

	# print( len( days_list ))
	days = list( set( days_list ) )
	# print( f'days= {days.sort()}' )
	# print( f'get_days → days → {days}' )
	return sorted( days )


def get_response_log( day ):
	global response_log
	# print('get_response_log')
	# print( len ( server.response_log ))
	# print( f'day = {day}' )
	select_log	= []
	for log in response_log:
		data = log['data']
		# print( f'data= {data}')
		date = data.split(" ")[0]
		# print( f'day={date}' )
		# days_list.append( date )
		if day == date:
			# print( f': {log}' )
			select_log.append( log )

	return select_log


def get_time():
	h = datetime.datetime.now().hour
	m = datetime.datetime.now().minute
	s = datetime.datetime.now().second
	return [h, m, s]


	# def on_message( client, userdata, msg ):

def messages( topic, payload ):
	# global zigbee_door_contact
	# global motion_time
	# global lux
	# a = s.split('=')
	# global mqtt_server_ip
	global location
	global alarm_set
	global response_log
	global VIP_IN
	global start_time
	global end_time
	global sensors_status
	s = datetime.datetime.now().second

	# topic = msg.topic
	if topic == 'location':
		location = payload

	if topic == 'start_time':
		# print('start_time ***********************************')
		start_time = json.loads( payload )

	if topic == 'end_time':
		end_time = json.loads( payload )

	if topic == 'alarm_set':
		alarm_set = False
		if payload == 'True':
			alarm_set = True

	if topic == 'VIP_IN':
		VIP_IN = json.loads( payload )
		print( f's VIP_IN: { VIP_IN }' )

	if topic == 'sensors_status':
		sensors_status = json.loads( payload )

	if topic == 'response_log':
		print(' flask → response_log')
		response_log = json.loads( payload )

	# if topic == 'keepalive':
	# 	mqtt_online_test_result()







# @app.route('/', methods=['GET', 'POST'])
@app.route('/')
def ss():
	global location
	global alarm_set
	global start_time
	global end_time
	global VIP_IN
	global sensors_status
	global response_log

	publish_command_mqtt('flask', 'update')
	mqtt_check_messages()

	select_log = []
	days = get_days( response_log )
	# print( f'days: {days}' )
	if days:
		select_log = get_response_log( days[-1] )

	# print( request.method )
	alarm_button	= ('Enable Alarm', 'Disable Alarm')[alarm_set]			# Deprecating alarm_button feature.
	alarm_status	= ('Alarm is not set', 'Alarm is set')[alarm_set]
	#patrol_button	= ('Patrol', 'At Ease')[patrol]
	# print( 'response_log = {}'.format( server.response_log ))

	# response_count_session	= len( response_log )							# Any new logs are automatically appended.
	# print( 'response_count_session ', response_count_session )

	# print( f'start_time = { start_time }' )

	start_time_hm			= '{}:{}'.format( start_time[0], start_time[1])
	end_time_hm				= '{}:{}'.format( end_time[0], end_time[1])

	return render_template('ss.html', location=location, alarm=alarm_button, alarm_status=alarm_status, select_log=select_log, days=days, VIP_IN=VIP_IN, start_time_hm=start_time_hm, end_time_hm=end_time_hm)
	# return 'Hello Dude'


@app.route('/d')
def ss_d():
	global location
	global alarm_set
	global start_time
	global end_time
	global VIP_IN
	global sensors_status
	global response_log
	global client

	publish_command_mqtt('flask', 'update')

	select_log = []
	days = get_days( response_log )
	# print( f'days: {days}' )
	if days:
		select_log = get_response_log( days[-1] )

	# print( request.method )
	alarm_button	= ('Enable Alarm', 'Disable Alarm')[alarm_set]			# Deprecating alarm_button feature.
	alarm_status	= ('Alarm is not set', 'Alarm is set')[alarm_set]
	#patrol_button	= ('Patrol', 'At Ease')[patrol]
	# print( 'response_log = {}'.format( server.response_log ))

	# response_count_session	= len( response_log )							# Any new logs are automatically appended.
	# print( 'response_count_session ', response_count_session )


	start_time_hm			= '{}:{}'.format( start_time[0], start_time[1])
	end_time_hm				= '{}:{}'.format( end_time[0], end_time[1])

	d = {
			'location': location,
			'alarm_set': alarm_set,
			'start_time': start_time,
			'end_time': end_time,
			'VIP_IN': VIP_IN,
			'sensors_status': sensors_status,
			'response_log - length': len( response_log )
		}

	return d


def ss_select( day ):
	global location
	global alarm_set
	global start_time
	global end_time
	global VIP_IN
	global sensors_status
	global response_log

	publish_command_mqtt('flask', 'update')
	mqtt_check_messages()

	select_log = []
	days = get_days( response_log )
	print( f'days: {days}' )
	if days:
		select_log = get_response_log( day )

	# print( request.method )
	alarm_button	= ('Enable Alarm', 'Disable Alarm')[alarm_set]			# Deprecating alarm_button feature.
	alarm_status	= ('Alarm is not set', 'Alarm is set')[alarm_set]
	#patrol_button	= ('Patrol', 'At Ease')[patrol]
	# print( 'response_log = {}'.format( server.response_log ))

	# response_count_session	= len( response_log )							# Any new logs are automatically appended.
	# print( 'response_count_session ', response_count_session )

	# print( f'start_time = { start_time }' )

	start_time_hm			= '{}:{}'.format( start_time[0], start_time[1])
	end_time_hm				= '{}:{}'.format( end_time[0], end_time[1])

	return render_template('ss.html', location=location, alarm=alarm_button, alarm_status=alarm_status, select_log=select_log, days=days, VIP_IN=VIP_IN, start_time_hm=start_time_hm, end_time_hm=end_time_hm)


@app.route('/selectday', methods=['GET', 'POST'])
def select_day():
	if request.method == 'POST':
		for key, val in request.form.items():
			print(key,val)
			if key == 'select_day':
				return ss_select( val )



	return 'Set time was submitted.'




# def backgroundSession_thread():
# 	# print("background Session_thread")
# 	global alarm_set
# 	# global shared_status
# 	global VIP_IN
# 	global response_log
#
# 	count = 0
# 	while True:
# 		print('Cooooooooooooooool')
# 		# print( f's: { shared_status['VIP_IN_dictionary'] }' )
# 		# check_alarm_schedule()
# 		# check_alarm_trigger()
# 		# check_doors()
# 		# check_event_log()
# 		# check_BLE( shared_status['VIP_IN_dictionary'] )
# 		check_BLE( VIP_IN )
# 		client.loop( 1 )


def check_BLE( VIP_IN_d ):
	#	Following 4 lines are commented out in case you click refresh.
	# if not server.BLE_notification:
	# 	return

	print( f's 128 VIP_IN: { VIP_IN_d }' )
	# server.BLE_notification = False
	print( 'BLE notification' )
	vip = []

	for i in VIP_IN_d:
		print( i )
		vip.append( str( i ) )

	print( f'vip = { vip }' )
	# socketio.emit( 'BLE', vip, namespace='/test', broadcast=True )


def check_alarm_schedule():
	# server.alarm_set
	global alarm_set_session



	# if alarm_set_session != server.alarm_set:
	# 	alarm_set_session = server.alarm_set
	#
	# 	alarm_status_update	= ('Alarm Not Set', 'Alarm Set')[server.alarm_set]
	# 	socketio.emit('toggle_alarm', alarm_status_update, namespace='/test', broadcast=True)
	# if alarm_set_session != alarm_set:
	# 	alarm_set_session = alarm_set
	#
	# 	alarm_status_update	= ('Alarm Not Set', 'Alarm Set')[alarm_set]
	# 	socketio.emit('toggle_alarm', alarm_status_update, namespace='/test', broadcast=True)



def publish_command_mqtt( topic, payload ):
	global mqtt

	mqtt.publish_command( topic, payload )


def mqtt_check_messages():
	global mqtt

	s = datetime.datetime.now().second
	messages_race = deepcopy( mqtt.messages )
	for i in messages_race.items():
		messages( i[0], i[1] )
		print( f'{s} { i[0] } { i[1] }' )

	mqtt.messages = {}			# May lose changes while iterating but avoiding a race condition.


if __name__ == '__main__':
	print('__main__')
	# socketio.run(app)
	# app.run(host='0.0.0.0', port='5000', debug=True)
	app.run(port=5000, debug=True, host='0.0.0.0', use_reloader=False)


# mqtt_subscribe()		#	This needs to be executed before client.loop( 1 ) is declared.


# def back_thread():
# 	while True:
# 		# print( '.' )
# 		mqtt_online_test()
# 		# publish_command('flask', 'update')
# 		# client.loop( 1 )
# 		time.sleep( 2 )

# t1 = threading.Thread( target = back_thread )
# t1.daemon = True
# t1.start()



if __name__ == '__main__':
    #call the functions here
	print( f'__name__ = {__name__}')
	app.run()
