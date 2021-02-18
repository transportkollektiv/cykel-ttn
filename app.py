import atexit
import os
import sys
import time

import requests
import ttn
from prometheus_client import Gauge, start_http_server

app_id = os.environ["TTN_APP_ID"]
access_key = os.environ["TTN_ACCESS_KEY"]
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


def uplink_callback(msg, client):
    try:
        print("Received uplink from %s" % (msg.dev_id))
        print(msg)
        data = msg.payload_fields
        update = {"device_id": msg.dev_id}
        if hasattr(data, "vbat"):
            update["battery_voltage"] = data.vbat
        if hasattr(data, "latitude") and hasattr(data, "longitude"):
            update["lat"] = data.latitude
            update["lng"] = data.longitude
        resp = requests.post(endpoint, headers=headers, data=update)
        print(resp)
        lbl = {"device_id": msg.dev_id, **promlabels}
        if data.vbat:
            voltgauge.labels(**lbl).set(data.vbat)
        timegauge.labels(**lbl).set(int(time.time()))
        packgauge.set(int(time.time()))
    except Exception as e:
        print(e)


def connect_callback(res, client):
    if not res:
        print("connection to ttn mqtt failed")
        client.close()
        sys.exit(1)
    else:
        print("connected to ttn")


handler = ttn.HandlerClient(app_id, access_key)
mqtt_client = handler.data()


def close_mqtt():
    mqtt_client.close()


atexit.register(close_mqtt)

mqtt_client.set_connect_callback(connect_callback)
mqtt_client.set_uplink_callback(uplink_callback)

print("starting cykel-ttn")
mqtt_client.connect()
start_http_server(port, addr=host)
print("serving metrics on %s:%s" % (host, port))

try:
    while 1:
        time.sleep(1)
except KeyboardInterrupt:
    print("exiting")
    sys.exit(0)
