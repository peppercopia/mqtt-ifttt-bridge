# Installing dependencies
# pip install requests
# pip install paho-mqtt
# pip install configparser

import requests
import paho.mqtt.client as mqtt
import configparser
from datetime import datetime


#Load in the configuration file
config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

# The callback for when the client receives a CONNACK response from the server.
def on_connect(self, client, userdata, rc):
    path = 'eventlog.txt'
    eventLog = open(path, 'a')
    print("Connected with result code "+str(rc))
    eventLog.write('********************* - Monitor Started - ****************************\n')
    eventLog.write('Monitor Start Time : ' + str(datetime.now()) + '\n')
    eventLog.write('*************************** - EOM - **********************************\n')
    eventLog.close()

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    self.subscribe(config['MQTT']['mqtt-topic-prefix'])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    api_key = config['IFTTT']['ifttt-api-key']
    event = config['IFTTT']['ifttt-event']
    value1 = str(msg.payload)
    value2 = 'Value 2' #Spare slots provided by IFTTT, not implemented
    value3 = 'Value 3' #Spare slots provided by IFTTT, not implemented
    url = 'https://maker.ifttt.com/trigger/{e}/with/key/{k}/'.format(e=event,k=api_key)
    payload = {'value1': value1, 'value2': value2, 'value3': value3}
    requests.post(url, data=payload)

    path = 'eventlog.txt'
    eventLog = open(path, 'a')
    eventLog.write('----------------------------------------------------------------------\n')
    eventLog.write('Time Event Received : ' + str(datetime.now()) + '\n')
    eventLog.write('----------------------------------------------------------------------\n')
    eventLog.write(str(msg.payload.decode("utf-8"))+ '\n')
    eventLog.write('----------------------------------------------------------------------\n')
    eventLog.write('*************************** - EOM - **********************************\n')
    eventLog.close()

# Get the MQTT values from the config
username = config['MQTT']['mqtt-username']
password = config['MQTT']['mqtt-password']
host = config['MQTT']['broker-url']
port = config.getint('MQTT', 'broker-port')

#Set up the MQTT client
client = mqtt.Client()
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message

#Connect to MQTT
client.connect(host, port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_forever()
