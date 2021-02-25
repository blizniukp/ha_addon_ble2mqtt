# -*- coding: utf-8 -*-

import getopt
import json
import logging
import paho.mqtt.client as mqtt
import sys
import time

CONFIG_PATH = "/data/options.json"
CONFIG = None
DEV_LIST = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s() - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(conf_path):
	with open(conf_path) as file:
		return json.load(file)


def get_dev_list(conf):
	devices = conf["devices"]
	dlist = []
	for device in devices:
		logger.info("Create new device: {}".format((str(device))))
		device['device_id'] = device["name"].replace(':', '_')
		d = {
			'name': device["name"],
			'address': device["address"],
			'address_type': device["address_type"],
			'service_uuid': device["service_uuid"],
			'char_uuid': device["char_uuid"]
		}
		dlist.append(d)
		logger.info("Append new element to dlist: {}".format(str(dlist)))
	return dlist


def create_switches(mqttc, conf):
	devices = conf["devices"]
	for device in devices:
		logger.info("Create new switch: {}".format((str(device))))
		topic = "homeassistant/switch/{}/config".format(device['device_id'])
		payload = {
			"name": device["name"],
			"unique_id": device['device_id'],
			"command_topic": "homeassistant/switch/{}/set".format(device['device_id']),
			"state_topic": "homeassistant/switch/{}/state".format(device['device_id'])
		}
		pub_message(mqttc, topic, json.dumps(payload))


def create_triggers(mqttc, conf):
	devices = conf["devices"]
	for device in devices:
		logger.info("Create new switch: {}".format((str(device))))
		topic = "homeassistant/device_automation/{}/config".format(device['device_id'])
		payload = {
			"automation_type": "trigger",
			"topic": "",
			"type": "button_short_press",
			"subtype": "button_1",
			"device": {
				"name": device["name"],
				"identifiers": [device['device_id']]
			}
		}
		pub_message(mqttc, topic, json.dumps(payload))


def pub_switch_status(mqttc, device, value):
	topic = "homeassistant/switch/{}/state".format(device['device_id'])
	payload = "ON" if int(value) == 1 else "OFF"
	pub_message(mqttc, topic, str(payload))


def pub_value(mqttc, payload):
	"""b'{"address": "F1:34:D5:DF:B8:3B", "is_notify": True, "val_len": 1, "val": 00}'"""
	global CONFIG
	vinfo = json.loads(payload.decode('utf-8'))
	devices = CONFIG["devices"]
	for device in devices:
		if device["address"] == vinfo["address"]:
			pub_switch_status(mqttc, device, vinfo["val"])
			return


def pub_message(mqttc, topic, payload):
	logger.info("Pub message. Topic: {}, payload: {}".format(topic, payload))
	mqttc.publish(topic, payload, qos=1)


def on_connect(mqttc, obj, flags, rc):
	logging.info("rc: " + str(rc))


def on_message(mqttc, obj, msg):
	logging.debug(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
	top = msg.topic.split('/')
	logging.info("Command: {}".format(top[3]))
	if top[3] == 'getDevList':
		resp = json.dumps(DEV_LIST)
		pub_message(mqttc, "/ble2mqtt/dev/devList", resp)
	if top[3] == 'value':
		logging.info("Receive value from device: {}".format(str(msg.payload)))
		pub_value(mqttc, msg.payload)


def on_publish(mqttc, obj, mid):
	logging.info("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
	logging.info("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
	logging.info(string)


def main(argv):
	global DEV_LIST
	global CONFIG
	logger.info("Start python script")

	logger.info("Load configuration")
	CONFIG = load_config(CONFIG_PATH)
	DEV_LIST = get_dev_list(CONFIG)

	logger.info("Config: {}".format(str(CONFIG)))
	logger.info("Device list: {}".format(str(DEV_LIST)))

	mqttc = mqtt.Client("Ble2Mqtt", clean_session=True)
	mqttc.on_message = on_message
	mqttc.on_connect = on_connect
	mqttc.on_publish = on_publish
	mqttc.on_subscribe = on_subscribe

	mqttc.username_pw_set(username=CONFIG["username"], password=CONFIG["password"])
	mqttc.connect(CONFIG['address'], int(CONFIG['port']), 60)
	logger.info("Connected to MQTT broker: {}".format(CONFIG['address']))

	mqttc.subscribe(CONFIG['sub_topic'], CONFIG['qos'])

	create_switches(mqttc, CONFIG)
	#create_triggers(mqttc, CONFIG)
	mqttc.loop_forever()
	logger.info("Stop python script")


if __name__ == "__main__":
	main(sys.argv[1:])
