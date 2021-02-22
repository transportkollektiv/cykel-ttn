import atexit
import json
import os
import sys
import time

import paho.mqtt.client as mqtt
import requests
from prometheus_client import Gauge, start_http_server

ttn_host = os.environ["TTN_HOST"]
ttn_username = os.environ["TTN_USERNAME"]
ttn_api_key = os.environ["TTN_API_KEY"]

endpoint = os.environ["ENDPOINT"]
auth_header = os.getenv("ENDPOINT_AUTH_HEADER", "")
port = int(os.getenv("PORT", 8080))
host = os.getenv("HOST", "")
labels = os.getenv("LABELS", None)

promlabels = {}
if labels is not None:
    promlabels = dict(s.split("=") for s in labels.split(","))

voltgauge = Gauge(
    "tracker_battery_volts",
    "tracker battery voltage",
    ["device_id"] + list(promlabels.keys()),
)
timegauge = Gauge(
    "tracker_last_data_update",
    "tracker last data timestamp",
    ["device_id"] + list(promlabels.keys()),
)
packgauge = Gauge("ttn_last_package_received", "last ttn package received timestamp")

headers = {}
if auth_header != "":
    headers = {"Authorization": auth_header}


def uplink_callback(msg):
    try:
        dev_id = msg["end_device_ids"]["device_id"]
        print("Received uplink from %s" % (dev_id))
        print(msg)
        data = msg["uplink_message"]["decoded_payload"]
        update = {"device_id": dev_id}
        if "vbat" in data:
            update["battery_voltage"] = data["vbat"]
        if "latitude" in data and "longitude" in data:
            update["lat"] = data["latitude"]
            update["lng"] = data["longitude"]
        resp = requests.post(endpoint, headers=headers, data=update)
        print(resp)
        lbl = {"device_id": dev_id, **promlabels}
        if "vbat" in data:
            voltgauge.labels(**lbl).set(data["vbat"])
        timegauge.labels(**lbl).set(int(time.time()))
        packgauge.set(int(time.time()))
    except Exception as e:
        print(e)


def on_connect(client, userdata, flags, rc):
    if rc > 0:
        print("connection to ttn mqtt failed")
        client.disconnect()
        sys.exit(1)

    print("connected to ttn")
    client.subscribe(f"v3/{ttn_username}/devices/+/up")


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode("utf-8"))
    uplink_callback(data)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(ttn_username, ttn_api_key)
# client.tls_set(ca_certs=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)

ttn_hostname, ttn_port = ttn_host.split(":")


def close_mqtt():
    # client.loop_stop()
    client.disconnect()


atexit.register(close_mqtt)

print("starting cykel-ttn")
client.connect(ttn_hostname, port=int(ttn_port), keepalive=60)
start_http_server(port, addr=host)
print("serving metrics on %s:%s" % (host, port))

client.loop_forever()
