# @socketio.on('connect', namespace='/test')
# def test_connect():
# 	global thread
# 	with thread_lock:
# 		if thread is None:
# 			thread = socketio.start_background_task(backgroundSession_thread)
# 			print( threading.currentThread().getName() )
# 			print( 'thread = {}'.format(thread.getName() ))
# 	emit('my_response', {'data': 'Connected', 'count': 0})
#
#
# @socketio.on('my_ping', namespace='/test')
# def ping_pong():
#     emit('my_pong')
#
#
# @socketio.on('set_start_time', namespace='/test')
# def set_start_time( message ):
# 	server.time_revised = True
# 	server.start_time_revised		= server.toListTime( message['data'] )
# 	subject = 'Set (Opening) Start Time: {}'.format( message['data'] )
# 	server.emit_response( subject )
# 	if server.alarm_triggered:
# 		reset_trigger()
#
#
# @socketio.on('set_end_time', namespace='/test')
# def set_end_time( message ):
# 	server.time_revised = True
# 	server.end_time_revised		= server.toListTime( message['data'] )
# 	subject = 'Set (Closing) End Time: {}'.format( message['data'] )
# 	server.emit_response( subject )
# 	if server.alarm_triggered:
# 		reset_trigger()
#
#
# @socketio.on('reset-trigger', namespace='/test')
# def reset_trigger():
# 	server.alarm_triggered = False
# 	server.door_triggered = 0				# May not need to reset this
# 	server.alarm_trigger_count = 0			# In case the alarm is running also needs to be reset if done auto
# 	server.emit_response( 'Trigger Reset.' )		# Add user name.
