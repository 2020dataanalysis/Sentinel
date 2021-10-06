from server_mqtt import MQTT
mqtt = MQTT()
# mqtt.get_ip()
print( mqtt.location )
mqtt.mqtt_subscribe()

mqtt.mqtt_online_test()
