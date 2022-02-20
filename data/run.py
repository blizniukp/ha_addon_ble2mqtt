# -*- coding: utf-8 -*-

import json
import logging
import paho.mqtt.client as mqtt
import sys


CONFIG_PATH = "/data/options.json"
CONFIG = None
DEV_LIST = None
SWITCH_LIST = None
MAX_BUTTON_PER_DEV = 6
MAX_BUTTON_FUNCTIONS = 3


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


def genearte_switch_list(device_list):
	slist = []
	for device in device_list:
		device_id = device["address"].replace(':', '_')
		for button_no in range(1, MAX_BUTTON_PER_DEV + 1):
			for func_no in range(1, MAX_BUTTON_FUNCTIONS + 1):
				b = {
					'dev_address': device_id,
					'name': device['name'] + '_B' + str(button_no) + '_F' + str(func_no),
					'unique_id': device_id + '_B' + str(button_no) + '_F' + str(func_no),
					'value_on': func_no,
					'value_off': 0,
				}
				slist.append(b)
	return slist


def create_switches(mqttc, switches):
	for switch in switches:
		logger.info("Create new switch: {}".format((str(switch))))
		topic = "homeassistant/switch/{}/config".format(switch['unique_id'])
		payload = {
			"name": switch["name"],
			"unique_id": switch['unique_id'],
			"command_topic": "homeassistant/switch/{}/set".format(switch['unique_id']),
			"state_topic": "homeassistant/switch/{}/state".format(switch['unique_id'])
		}
		pub_message(mqttc, topic, json.dumps(payload))


def pub_switch_status(mqttc, switch, button_value):
	topic = "homeassistant/switch/{}/state".format(switch['unique_id'])
	payload = "OFF" if button_value == 0 else "ON"
	pub_message(mqttc, topic, str(payload))


def parse_and_pub_value(mqttc, payload):
	global SWITCH_LIST
	vinfo = json.loads(payload.decode('utf-8'))
	device_id = vinfo["address"].replace(':', '_')
	button_data = int(vinfo["val"][:2])
	button_no = button_data // 10
	func_no = button_data % 10
	button_value = int(vinfo["val"][2:4])
	unique_id = device_id + '_B' + str(button_no) + '_F' + str(func_no)
	for switch in SWITCH_LIST:
		if str(switch["unique_id"]) == str(unique_id):
			logger.info("Publish switch status. Switch: {}, value: {}".format(str(switch), str(button_value)))
			pub_switch_status(mqttc, switch, button_value)
			return


def pub_message(mqttc, topic, payload):
	logger.info("Pub message. Topic: {}, payload: {}".format(topic, payload))
	mqttc.publish(topic, payload, qos=1)


def on_connect(mqttc, obj, flags, rc):
	logger.info("rc: " + str(rc))


def on_message(mqttc, obj, msg):
	logger.debug(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
	top = msg.topic.split('/')
	logger.info("Command: {}".format(top[3]))
	if top[3] == 'getDevList':
		resp = json.dumps(DEV_LIST)
		pub_message(mqttc, "/ble2mqtt/dev/devList", resp)
	if top[3] == 'value':
		logger.info("Receive value from device: {}".format(str(msg.payload)))
		parse_and_pub_value(mqttc, msg.payload)


def on_publish(mqttc, obj, mid):
	logger.info("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
	logger.info("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
	logger.info(string)


def main(argv):
	global DEV_LIST
	global CONFIG
	global SWITCH_LIST
	logger.info("Start python script")

	try:
		logger.info("Load configuration")
		CONFIG = load_config(CONFIG_PATH)
		DEV_LIST = get_dev_list(CONFIG)
		SWITCH_LIST = genearte_switch_list(DEV_LIST)

		logger.info("Config: {}".format(str(CONFIG)))
		logger.info("Device list: {}".format(str(DEV_LIST)))
		logger.info("Switch list: {}".format(str(SWITCH_LIST)))

		mqttc = mqtt.Client("Ble2Mqtt", clean_session=True)
		mqttc.on_message = on_message
		mqttc.on_connect = on_connect
		mqttc.on_publish = on_publish
		mqttc.on_subscribe = on_subscribe

		mqttc.username_pw_set(username=CONFIG["username"], password=CONFIG["password"])
		mqttc.connect(CONFIG['address'], int(CONFIG['port']), 60)
		logger.info("Connected to MQTT broker: {}".format(CONFIG['address']))

		mqttc.subscribe(CONFIG['sub_topic'], CONFIG['qos'])

		create_switches(mqttc, SWITCH_LIST)
		mqttc.loop_forever()
		logger.info("Stop python script")
	except Exception as ex:
		logger.exception(ex)


if __name__ == "__main__":
	main(sys.argv[1:])
