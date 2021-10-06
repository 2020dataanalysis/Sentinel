#	Terminal commands:
#	command/office/doors/terminal
#	command/office/terminal

#	clear
#	print=0,0,5,0,Alarm Set
#	print=0,0,4,0,Alarm Not Set
#	Need 40 vertical space to next line down.
#	print=0,40,5,0,Rich
#	print=0,80,5,0,Keith
#	flash=31  → Blue
#	flash=63488 → Red
#	flash=2016	→ Green
#	flash=65535	→ White
#	flash=0		→ Black
#	flash=65535, 31

#	Door Protocol:
#		Door Monitor sends a message when door opens & closes.
#		See code.
#	If you get a list index out of range error then mqtt crashes with out warning.


import os, time, datetime, threading, smtplib, requests, urllib, shutil
import paho.mqtt.client as mqtt

	#	================================================================
	#	==========================		MQTT	========================
	#	================================================================

class MQTT:
	def __init__( self, client_id ):
		self.client = None
		self.client_id = client_id
		self.online_lapse_time = int( time.time() )
		self.active_keep_alive_test = False
		self.get_ip()
		self.subscribe_list = []
		self.messages = {}
		self.alive = False

	def get_ip( self ):
		from subprocess import check_output
		# print check_output(['hostname', '-I'])
		a = check_output(['hostname', '-I'])
		ip = a.split()
		# print( ip[0] )

		self.server_ip	= ip[0].decode("utf-8")
		# print( type( mqtt_server_ip ) )
		self.location = 'bear'
		if self.server_ip == '10.0.0.12':
			self.location = "blackhawk"


	def get_time( self ):
		h = datetime.datetime.now().hour
		m = datetime.datetime.now().minute
		s = datetime.datetime.now().second
		return [h, m, s]


	def mqtt_online_test( self ):
		t		= int( time.time() )
		lapse	= t - self.online_lapse_time
		if not self.alive:
			return False

		if not self.active_keep_alive_test:
			if lapse > 60:
				self.active_keep_alive_test = True
				# online_lapse_time = int( time.time() )
				# print( f'MQTT: { self.get_time() } Online Lapse Time Test { lapse }' )
				self.publish_command( 'online', str( t ) + ' - lapse = ' + str( lapse ) )

		if lapse > 90:
			self.active_keep_alive_test = False
			print('MQTT: mqtt failed to receive - online Lapse Time > 90 → Fail')
			self.online_lapse_time = t
			self.alive = False
			self.client.loop_stop()
			self.client.disconnect()
			self.mqtt_subscribe()
			return False

		return True


	def mqtt_online_test_result( self ):
		self.active_keep_alive_test = False
		# print( f'MQTT: { self.get_time() } Online Test Result → Running' )
		self.online_lapse_time = int( time.time() )


	def add_subscribe( self, topic ):
		self.subscribe_list.append( topic )

	def on_connect( self, client, userdata, flags, rc ):
		print( f'MQTT: Connected with result code {rc}' )
		for i in self.subscribe_list:
			client.subscribe( i )

	def on_log( self, client, userdata, level, buf ):
		pass
		# print( 'log: ' + buf )


	def on_message( self, client0, userdata, msg ):
		# print( msg.qos ) → 0
		payload = msg.payload.decode('utf-8')
		s = datetime.datetime.now().second
		print( f'MQTT: on_message: {s} {msg.topic} {payload}' )

		if msg.topic == 'online':
			self.mqtt_online_test_result()
		else:
			self.messages[ msg.topic ] = payload


	def mqtt_subscribe( self ):
		self.client = mqtt.Client(client_id=self.client_id, clean_session=True)		# 06/28/2021
		self.client.on_connect	= self.on_connect
		self.client.on_message	= self.on_message
		self.client.on_log		= self.on_log
		self.client.connect( self.server_ip, 1883, 60 )
		# client.reconnect_delay_set(min_delay=1, max_delay=120)
		self.client.loop_start()
		print( f'MQTT: { self.client }' )
		self.alive = True


	def publish_command( self, topic, payload ):
		self.client.publish( topic, payload=payload, qos=0, retain=True )		# 06/28/2021
