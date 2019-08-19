import time
import ttn
import sys
import atexit
import requests
import os

app_id = os.env['TTN_APP_ID']
access_key = os.env['TTN_ACCESS_KEY']
endpoint = os.env['ENDPOINT']

def uplink_callback(msg, client):
	try:
		print("Received uplink from ", msg.dev_id)
		print(msg)
		bike_number = msg.dev_id.replace("tbeam-cccamp-", "")
		data = msg.payload_fields
		update = {
			'bike_number': bike_number,
			'lat': data.latitude,
			'lng': data.longitude
		}
		resp = requests.post(endpoint, data=update)
		print(resp)
	except e:
		print(e)

handler = ttn.HandlerClient(app_id, access_key)
mqtt_client = handler.data()

def close_mqtt():
	mqtt_client.close()

atexit.register(close_mqtt)

mqtt_client.set_uplink_callback(uplink_callback)
mqtt_client.connect()

try:
	while 1:
		time.sleep(1)
except KeyboardInterrupt:
	print('exiting')
	sys.exit(0)
