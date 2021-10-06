from flask import request, render_template, session
from flask import url_for, g, session, redirect
from flask_socketio import SocketIO, emit, disconnect
# import server
from s import app, socketio


#	sudo pip install flask-wtf
from flask_wtf.csrf import CSRFError

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400




# #	Exact copy of patrol_public except snapshots
# @app.route('/s', methods=['GET', 'POST'])
# def remote_test():
# 	global response_count_session		# May chanage later.  May not have had a chance to update.?
#
# 	select_log = []
# 	days = get_days()
# 	# print( f'days: {days}' )
# 	if days:
# 		select_log = get_response_log( days[-1] )
#
# 	# print( request.method )
# 	alarm_button	= ('Enable Alarm', 'Disable Alarm')[server.alarm_set]			# Deprecating alarm_button feature.
# 	alarm_status	= ('Alarm is not set', 'Alarm is set')[server.alarm_set]
# 	#patrol_button	= ('Patrol', 'At Ease')[patrol]
# 	# print( 'response_log = {}'.format( server.response_log ))
#
# 	response_count_session	= len( server.response_log )							# Any new logs are automatically appended.
# 	# print( 'response_count_session ', response_count_session )
# 	start_time_hm			= '{}:{}'.format(server.start_time[0], server.start_time[1])
# 	end_time_hm				= '{}:{}'.format(server.end_time[0], server.end_time[1])
# 	# return render_template('patrol_public_snapshots.html', async_mode=socketio.async_mode, alarm=alarm_button, alarm_status=alarm_status, response_log=select_log, days=days, start_time_hm=start_time_hm, end_time_hm=end_time_hm)
# 	return render_template('test.html', async_mode=socketio.async_mode, location=server.location, alarm=alarm_button, alarm_status=alarm_status, select_log=select_log, days=days, start_time_hm=start_time_hm, end_time_hm=end_time_hm)













@app.route('/login',	methods=['GET', 'POST'])
@app.route('/login.html',	methods=['GET', 'POST'])
def login():
	print ( {'ip': request.remote_addr}, 200 )
	if request.method == 'POST':
		session.pop('user', None)

	return render_template('/login.html')


# @app.route('/settings', methods=['GET', 'POST'])
# def settings():
# 	# print( request.method )
#
# 	if request.method != 'POST':
# 		return render_template('/login.html' )
#
# 	# if not 'user' in session:
# 	# 	return 'Return from where you crept !'
# 	#
# 	# if session['user'] != 'sam':
# 	# 	return session['user'] + ', your hacking is improving !'
# 	week = ['Monday', 'Teusday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
# 	return render_template('/settings.html', week=week, users=server.users, recipients=server.recipients, arm_period=server.arm_period, confirmation = server.confirmation )


# @app.route('/', methods=['GET', 'POST'])
# def patrol_public():
# 	global response_count_session		# May chanage later.  May not have had a chance to update.?
#
# 	days = get_days()
# 	select_log = get_response_log( days[-1] )
#
# 	# print( request.method )
# 	alarm_button	= ('Enable Alarm', 'Disable Alarm')[server.alarm_set]			# Deprecating alarm_button feature.
# 	alarm_status	= ('Alarm is not set', 'Alarm is set')[server.alarm_set]
# 	#patrol_button	= ('Patrol', 'At Ease')[patrol]
# 	# print( 'response_log = {}'.format( server.response_log ))
# 	response_count_session = len( server.response_log )
# 	start_time_hm = '{}:{}'.format(server.start_time[0], server.start_time[1])
# 	end_time_hm = '{}:{}'.format(server.end_time[0], server.end_time[1])
# 	return render_template('patrol_public.html', async_mode=socketio.async_mode, alarm=alarm_button, alarm_status=alarm_status, select_log=select_log, start_time_hm=start_time_hm, end_time_hm=end_time_hm)


#	Exact copy of patrol_public except snapshots
@app.route('/ss', methods=['GET', 'POST'])
def patrol_public_snapshots():
	global response_count_session		# May chanage later.  May not have had a chance to update.?
	# global shared_status

	select_log = []
	# days = get_days()
	# # print( f'days: {days}' )
	# if days:
	# 	select_log = get_response_log( days[-1] )
	#
	# # print( request.method )
	# alarm_button	= ('Enable Alarm', 'Disable Alarm')[server.alarm_set]			# Deprecating alarm_button feature.
	# alarm_status	= ('Alarm is not set', 'Alarm is set')[server.alarm_set]
	# #patrol_button	= ('Patrol', 'At Ease')[patrol]
	# # print( 'response_log = {}'.format( server.response_log ))
	#
	# response_count_session	= len( server.response_log )							# Any new logs are automatically appended.
	# # print( 'response_count_session ', response_count_session )
	# start_time_hm			= '{}:{}'.format(server.start_time[0], server.start_time[1])
	# end_time_hm				= '{}:{}'.format(server.end_time[0], server.end_time[1])
	# return render_template('patrol_public_snapshots.html', async_mode=socketio.async_mode, alarm=alarm_button, alarm_status=alarm_status, response_log=select_log, days=days, start_time_hm=start_time_hm, end_time_hm=end_time_hm)
	# return render_template('patrol_public_snapshots.html', async_mode=socketio.async_mode, location=server.location, alarm=alarm_button, alarm_status=alarm_status, select_log=select_log, days=days, start_time_hm=start_time_hm, end_time_hm=end_time_hm)
	# return render_template('patrol_public_snapshots.html', async_mode=socketio.async_mode, location='Blackhawk', alarm=alarm_button, alarm_status=alarm_status, select_log=select_log, days=days, start_time_hm=start_time_hm, end_time_hm=end_time_hm)
	# return shared_status

	b = shared_status['alarm_set']
	if b:
		return 'True Dat'
	else:
		return 'False Dat'
	# return 'Cool'










def get_days( ):
	# print('get_days')
	# print( len( server.response_log ))
	days_list = []
	for log in server.response_log:
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


# def get_response_log( day ):
# 	# print('get_response_log')
# 	# print( len ( server.response_log ))
# 	# print( f'day = {day}' )
# 	select_log	= []
# 	for log in server.response_log:
# 		data = log['data']
# 		# print( f'data= {data}')
# 		date = data.split(" ")[0]
# 		# print( f'day={date}' )
# 		# days_list.append( date )
# 		if day == date:
# 			# print( f': {log}' )
# 			select_log.append( log )
#
# 	return select_log


def relog_event2( count, timestamp, subject ):
	# global response_log
	# global response_count

	log = []
	message = timestamp + "→ " + subject
	# response_count += 1
	d = {'data': message, 'count': count + 1 }
	log.append( d )
	return log


# @app.route('/settings/save', methods=['GET', 'POST'])
# def settings_save():
#
# 	print ( request.method )
# 	#	Convert string to dictionary.
# 	server.users = eval( request.form['users'] )
# 	server.recipients = request.form['recipients_email']
#
# 	server.confirmation = ''
# 	if 'confirmation' in request.form.keys():
# 		server.confirmation = 'checked'
#
# 	week = ['Monday', 'Teusday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
# 	f = open('security/credentials.py', 'w')
# 	f.write('users=' + request.form['users'] + '\n')
#
# 	print( request.form['users'] )
# 	print( request.form['recipients_email'] )
# 	f.write('recipients=' + request.form['recipients_email'] + '\n')
# 	f.write('confirmation = \'' + server.confirmation +'\'\n')
# 	f.write('arm_period={\n')
# 	d = {}
# 	c = ','
# 	for day in week:
# 		print(day)
# 		l = []
# 		l.append(  request.form['start_time_' + day] )
# 		l.append(  request.form['end_time_' + day] )
#
# 		if day == 'Sunday':
# 			c = ''
#
# 		d[day] = l
# 		f.write('\t\'' + day + '\':' + str(l) + c + '\n')
#
# 	f.write('}\n')
# 	f.close()
#
# 	server.arm_period = d
# 	print( server.arm_period )
# 	return render_template('/login.html')


# @app.route('/security', methods=['GET', 'POST'])
# def security():
# 	global response_count_session		# May chanage later.  May not have had a chance to update.?
# 	print('security')
# 	# print( request.method )
#
# 	if request.method == 'POST':
# 		if request.form['username'] not in server.users.keys():
# 			return redirect( url_for('login'))
#
# 		if server.users[request.form['username']] != request.form['password']:
# 			return redirect( url_for('login'))
#
# 		session['user'] = request.form['username']
# 		g.user = None
# 		if 'user' in session:
# 			g.user = session['user']
#
# 		if not g.user:
# 			return 'Return from where you crept !'
#
#
# 	else:
# 		parameters = request.url.split('?')[1]
# 		print( parameters )
# 		user = parameters.split('&')[0].split('=')[1]
# 		password = parameters.split('&')[1].split('=')[1]
# 		print( user )
# 		print( password )
# 		if user != 'VIP':
# 			#return render_template('/login.html')
# 			return 'Invalid access codes.'
#
# 		if password != server.token_password:
# 			return 'Invalid access codes.'
#
# 		session['user'] = user
#
# 	alarm_button	= ('Enable Alarm', 'Disable Alarm')[server.alarm_set]			# Deprecating alarm_button feature.
# 	alarm_status	= ('Alarm is not set', 'Alarm is set')[server.alarm_set]
# 	#patrol_button	= ('Patrol', 'At Ease')[patrol]
# 	# print( 'response_log = {}'.format( server.response_log ))
# 	response_count_session = len( server.response_log )
# 	start_time_hm 	= '{}:{}'.format(server.start_time[0], server.start_time[1])
# 	end_time_hm 	= '{}:{}'.format(server.end_time[0], server.end_time[1])
#
# 	# print( request.user_agent )
# 	os = str( request.user_agent ).split(' (')[1].split(';')[0]
# 	print( os )
# 	if os == 'iPhone':
# 		return render_template('patrol_iphone.html', async_mode=socketio.async_mode, alarm=alarm_button, alarm_status=alarm_status, response_log=server.response_log, start_time_hm=start_time_hm, end_time_hm=end_time_hm)
# 	else:
# 		return render_template('patrol.html', async_mode=socketio.async_mode, alarm=alarm_button, alarm_status=alarm_status, response_log=server.response_log, start_time_hm=start_time_hm, end_time_hm=end_time_hm)


# @app.route('/iphone_set_alarm', methods=['GET', 'POST'])
# def iphone_set_time():
# 	print( 'iphone_set_alarm - ***********************************' )
# 	if request.method == 'POST':
# 		for key, val in request.form.items():
# 			print(key,val)
# 			if key == 'start_time':
# 				d = {'data': val}
# 				super().set_start_time( d )
#
# 			if key == 'end_time':
# 				d = {'data': val}
# 				super().set_end_time( d )
#
# 	return 'Set time was submitted.'


@app.route('/help', methods=['GET', 'POST'])
def help():
	# if request.form['username'] not in users.keys():
	# 	return redirect( url_for('login'))
	#
	# if users[request.form['username']] != request.form['password']:
	# 	return redirect( url_for('login'))
	#
	# session['user'] = request.form['username']
	# g.user = None
	# if 'user' in session:
	# 	g.user = session['user']
	#
	# if not g.user:
	# 	return 'Return from where you crept !'
	return render_template('help.html')


@app.route('/i2',	methods=['GET', 'POST'])
def i2():
	print ( {'ip': request.remote_addr}, 200 )
	# if request.method == 'POST':
	# 	session.pop('user', None)
	#print( request.user_agent )
	os = str( request.user_agent ).split(' (')[1].split(';')[0]
	print( f'[{os}]' )
	# if os == 'iPhone':
	return render_template('/iphone2.html')


@app.route('/image')
def index():
	# generate_img("t.jpg"); #save inside static folder
	return '<img src=' + url_for('static', filename='t.jpg') + '>'
