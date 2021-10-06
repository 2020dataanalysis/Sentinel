import paho.mqtt.client as mqtt
import time, datetime
import json


client = None		# MQTT
zigbee_door_contact = True
# mqtt_server_ip	= '10.0.0.12'


from subprocess import check_output
# print check_output(['hostname', '-I'])
a = check_output(['hostname', '-I'])
ip = a.split()
print( ip[0] )

mqtt_server_ip	= ip[0].decode("utf-8")
print( type( mqtt_server_ip ))
location = "bear"
if mqtt_server_ip == '10.0.0.12':
	location = "blackhawk"


VIP_IN = {}
response_log = []

#	================================================================
#	==========================		MQTT	========================
#	================================================================
def mqtt_subscribe():
	global client
	global mqtt_server_ip

	# import paho.mqtt.client as mqtt

	def on_connect( client0, userdata, flags, rc ):
		global client

		print( f'Connected with result code {rc}' )
		client.subscribe( 'office/door1' )
		client.subscribe( 'office/door2' )
		client.subscribe( 'office' )
		client.subscribe( 'shop' )
		client.subscribe( 'zigbee2mqtt/0x286d9700010d9cd0' )
		client.subscribe( 'alarm_set' )
		client.subscribe( 'VIP_IN' )
		client.subscribe( 'start_time' )
		client.subscribe( 'end_time' )
		client.subscribe( 'response_log' )


	def on_message( client0, userdata, msg ):
		global mqtt_server_ip
		global response_log
		global VIP_IN
		# global client

		# print( msg.qos ) → 0
		payload = msg.payload.decode('utf-8')
		s = datetime.datetime.now().second
		print( f'{s} {msg.topic} {payload}' )

		topic = msg.topic
		if topic == 'alarm_set':
			server_alarm_set = False
			if payload == 'True':
				server_alarm_set = True

		if topic == 'VIP_IN':
			VIP_IN = json.loads( payload )
			print( f's VIP_IN: { VIP_IN }' )



		if topic == 'response_log':
			print(' flask → response_log')
			# import json
			# print( response_log )
			response_log = json.dumps( response_log )
			print( response_log )
			# client.publish( 'flask', payload=json_response_log, qos=0, retain=False )
		# messages( msg.topic, payload )


	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message

	client.connect( mqtt_server_ip, 1883, 60 )
	print( client )


mqtt_subscribe()
print( location )

def messages( topic, s ):
	global zigbee_door_contact
	global motion_time
	global lux

	a = s.split('=')
	print( f'Topic={topic} → message={ a }' )



while True:
	print('.')
	client.loop( 1 )
	time.sleep( 1 )
