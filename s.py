import threading, logging, requests, urllib, datetime
from threading import Lock
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
#
app = Flask(__name__)
app.config['SECRET_KEY'] = 'MayDay'
socketio = SocketIO(app, async_mode = None )
thread = None
thread_lock = Lock()

alarm_set_session = False
alarm_triggered_session = False
response_count_session = 0

import ftp_snapshot
import server
from route import *

#		You need to create a thread so parent thread can serve pages
t1 = threading.Thread( target = server.background_scheduler )
t1.daemon = True
t1.start()


def backgroundSession_thread():
	# print("background Session_thread")
	global alarm_set_session

	alarm_set_session = server.alarm_set
	count = 0
	while True:
		check_alarm_schedule()
		check_alarm_trigger()
		check_doors()
		check_event_log()
		check_BLE()
		socketio.sleep(1)


def check_BLE():
	#	Following 4 lines are commented out in case you click refresh.
	# if not server.BLE_notification:
	# 	return

	# server.BLE_notification = False
	# print( 'BLE notification' )
	vip = []
	for i in server.ble.VIP_IN_dictionary:
		vip.append( str( i ) )

	socketio.emit('BLE', vip, namespace='/test', broadcast=True)


def check_alarm_schedule():
	# server.alarm_set
	global alarm_set_session

	if alarm_set_session != server.alarm_set:
		alarm_set_session = server.alarm_set

		alarm_status_update	= ('Alarm Not Set', 'Alarm Set')[server.alarm_set]
		socketio.emit('toggle_alarm', alarm_status_update, namespace='/test', broadcast=True)


def check_alarm_trigger():
	global alarm_triggered_session

	# print( server.alarm_triggered )
	if server.alarm_triggered != alarm_triggered_session:
		alarm_triggered_session = server.alarm_triggered
		#alarm_status	= ('Alarm is not set', 'Alarm is set')[alarm_set]
		subject			= ('Alarm Intruder Alert Deactivated', 'Alarm Intruder Alert is Triggered !')[alarm_triggered_session]
		server.emit_response( subject )

		if server.alarm_triggered:
			socketio.emit('alarm_triggered', namespace='/test', broadcast=True)
		else:
			socketio.emit('alarm_reset', namespace='/test', broadcast=True)


def check_doors():
	# print( server.sensors_status )
	socketio.emit('status', server.sensors_status, namespace='/test')


def check_event_log():
	global response_count_session

	for i in range( response_count_session, len( server.response_log )):
		d = server.response_log[i]
		socketio.emit('my_response', d, namespace='/test', broadcast=True)

	response_count_session = len( server.response_log )




@socketio.on('mqtt_publish', namespace='/test')
def remote_test_command_publish( message ):
	print( message['topic'] )
	print( message['payload'] )
	server.publish_command( message['topic'], message['payload'] )




@socketio.on('connect', namespace='/test')
def test_connect():
	global thread
	with thread_lock:
		if thread is None:
			thread = socketio.start_background_task(backgroundSession_thread)
			print( threading.currentThread().getName() )
			print( 'thread = {}'.format(thread.getName() ))
	emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('set_start_time', namespace='/test')
def set_start_time( message ):
	server.time_revised = True
	server.start_time_revised		= server.toListTime( message['data'] )
	subject = 'Set (Opening) Start Time: {}'.format( message['data'] )
	server.emit_response( subject )
	if server.alarm_triggered:
		reset_trigger()


@socketio.on('set_end_time', namespace='/test')
def set_end_time( message ):
	server.time_revised = True
	server.end_time_revised		= server.toListTime( message['data'] )
	subject = 'Set (Closing) End Time: {}'.format( message['data'] )
	server.emit_response( subject )
	if server.alarm_triggered:
		reset_trigger()


@socketio.on('reset-trigger', namespace='/test')
def reset_trigger():
	server.alarm_triggered = False
	server.door_triggered = 0				# May not need to reset this
	server.alarm_trigger_count = 0			# In case the alarm is running also needs to be reset if done auto
	server.emit_response( 'Trigger Reset.' )		# Add user name.


@socketio.on('request_log', namespace='/test')
def request_log( message ):
	# print('request_log')
	day			= message['data']
	select_log = get_response_log( day )
	socketio.emit('zrequest_log_response', select_log, namespace='/test')


@app.route('/iphone_set_alarm', methods=['GET', 'POST'])
def iphone_set_time():
	print( 'iphone_set_alarm' )
	if request.method == 'POST':
		for key, val in request.form.items():
			print(key,val)
			if key == 'start_time':
				d = {'data': val}
				set_start_time( d )

			if key == 'end_time':
				d = {'data': val}
				set_end_time( d )

	return 'Set time was submitted.'

# if __name__ == '__main__':
# 	socketio.run(app)
# 	#app.run(host='0.0.0.0', port='5000', debug=True)
# 	#app.run(port=5000, debug=config.DEBUG, host='0.0.0.0', use_reloader=False)
