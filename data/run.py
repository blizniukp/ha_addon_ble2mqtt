# -*- coding: utf-8 -*-

import getopt
import json
import logging
import paho.mqtt.client as mqtt
import sys
import time

CONFIG_PATH = "/data/options.json"
CONFIG = None

dev_list = [
	{
		'name': 'Nordic_Blinky',
		'address': 'F1:34:D5:DF:B8:3B',
		'address_type': 'public',
		'service_uuid': "00001523-1212-EFDE-1523-785FEABCD123",
		'char_uuid': "00001524-1212-EFDE-1523-785FEABCD123"
	}
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s() - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config():
	with open(CONFIG_PATH) as file:
		return json.load(file)


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
		resp = json.dumps(dev_list)
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
	logger.info("Start python script")

	logger.info("Load configuration")
	CONFIG = load_config()

	logger.info("Config: {}".format(str(CONFIG)))

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
