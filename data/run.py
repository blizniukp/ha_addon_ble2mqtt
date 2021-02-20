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

	mqttc = mqtt.Client()
	mqttc.on_message = on_message
	mqttc.on_connect = on_connect
	mqttc.on_publish = on_publish
	mqttc.on_subscribe = on_subscribe

	mqttc.username_pw_set(username=CONFIG["username"], password=CONFIG["password"])
	mqttc.connect(CONFIG['address'], int(CONFIG['port']), 60)
	logger.info("Connected to MQTT broker: {}".format(CONFIG['address']))

	mqttc.subscribe(CONFIG['sub_topic'], CONFIG['qos'])

	mqttc.loop_forever()
	logger.info("Stop python script")


if __name__ == "__main__":
	main(sys.argv[1:])
