import time
import ttn
import sys
import atexit
import requests
import os

from prometheus_client import Gauge, start_http_server

app_id = os.environ['TTN_APP_ID']
access_key = os.environ['TTN_ACCESS_KEY']
endpoint = os.environ['ENDPOINT']
port = int(os.getenv('PORT', 8080))
host = os.getenv('HOST', '')

voltgauge = Gauge('bike_battery_volts', 'bike battery voltage', ['bike_number'])
timegauge = Gauge('bike_last_data_update', 'bike last data timestamp', ['bike_number'])
packgauge = Gauge('ttn_last_package_received', 'last ttn package received timestamp')

def uplink_callback(msg, client):
	try:
		print("Received uplink from ", msg.dev_id)
		print(msg)
		bike_number = msg.dev_id.replace("tbeam-cccamp-", "")
		data = msg.payload_fields
		update = {
			'bike_number': bike_number,
			'lat': data.latitude,
			'lng': data.longitude,
			'battery_voltage': data.vbat
		}
		resp = requests.post(endpoint, data=update)
		print(resp)
		voltgauge.labels(bike_number=bike_number).set(data.vbat)
		timegauge.labels(bike_number=bike_number).set(int(time.time()))
		packgauge.set(int(time.time()))
	except e:
		print(e)


handler = ttn.HandlerClient(app_id, access_key)
mqtt_client = handler.data()

def close_mqtt():
	mqtt_client.close()

atexit.register(close_mqtt)

mqtt_client.set_uplink_callback(uplink_callback)
mqtt_client.connect()

start_http_server(port, addr=host)

print('starting cykel-ttn')
print('serving metrics on %s:%s' % (host, port))

try:
	while 1:
		time.sleep(1)
except KeyboardInterrupt:
	print('exiting')
	sys.exit(0)
