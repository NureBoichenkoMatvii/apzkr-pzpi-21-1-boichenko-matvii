from libs.mqtt_client import ApiBridgeClient
import argparse
import logging
import os
import sys
import time
from dotenv import load_dotenv

# Read in command-line parameters
parser = argparse.ArgumentParser()
# parser.add_argument("-env", "--environment", action="store", required=True, dest="ENV", help="Environment name")
parser.add_argument("-cid", "--clientId", action="store", dest="CLIENT_ID", help="Id of client to connect with")
parser.add_argument("-u", "--mqttUser", action="store", dest="MQTT_USER", help="Username to use during connect to MQTT broker")
parser.add_argument("-p", "--mqttPassword", action="store", dest="MQTT_PASS", help="Password to use during connect to MQTT broker")
parser.add_argument("-mbh", "--mqttBrokerHost", action="store", dest="MQTT_BROKER_HOST", help="MQTT broker's host to connect to")
parser.add_argument("-ah", "--apiHost", action="store", dest="HTTP_API_HOST", help="Base endpoint/common name for API endpoints to which redirects will happen")
parser.add_argument("-ak", "--apiKey", action="store", dest="HTTP_API_KEY", help="String key/secret to send in X-Api-Key header to authorize requests")

load_dotenv("./.env", verbose=True)

args = parser.parse_args()
for k, v in args.__dict__.items():
    if v:
        os.environ[k] = v

logger = logging.getLogger(f"Client_{os.environ['CLIENT_ID']}")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Uncomment for getting logs in a view of the file
# file_handler = logging.FileHandler(filename=f"tmp_{os.environ['CLIENT_ID']}.log")
# logger.addHandler(file_handler)

client = ApiBridgeClient(logger)
client.connect_client()

# Blocking call that processes network traffic, dispatches callbacks, and handles reconnecting.
while True:
    time.sleep(5)
    client.loop()
# client.mqtt_client.loop_forever()
