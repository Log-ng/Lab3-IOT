print("Xin chào ThingsBoard")
import paho.mqtt.client as mqttclient
import time
import json

import serial.tools.list_ports

mess = ""
bbc_port = "COM3"
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)

import subprocess as sp
import re
# --------------------------------------------------------------------------
wt = 5 # Wait time -- I purposefully make it wait before the shell command
accuracy = 3 #Starting desired accuracy is fine and builds at x1.5 per loop
# --------------------------------------------------------------------------
BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "cOHFSdk5cNGKr45SAdvB"

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    return splitData   # add
def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            datalist = processData(mess[start:end + 1])
            
            collect_data = {'temperature': datalist[2]} if datalist[1] == "TEMP" else {'humidity': datalist[2]}              #test
            client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)    #test
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]

def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd = 1
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLed":
            temp_data['value'] = jsonobj['params']
            # client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            client.publish('v1/devices/me/Button-Led-again', json.dumps(temp_data), 1)
            cmd = 1 if jsonobj['params'] else 0 
            print("cmd test", cmd)
        elif jsonobj['method'] == "setPump":
            temp_data['value'] = jsonobj['params']
            # client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            client.publish('v1/devices/me/Button-Pump', json.dumps(temp_data), 1)
            cmd = 2 if jsonobj['params'] else 3 
    except:
        pass
    if len(bbc_port) > 0:
        ser.write((str(cmd) + "#").encode())

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")
def get_location():
    pshellcomm = ['powershell']
    pshellcomm.append('add-type -assemblyname system.device; ' \
                      '$loc = new-object system.device.location.geocoordinatewatcher;' \
                      '$loc.start(); ' \
                      'while(($loc.status -ne "Ready") -and ($loc.permission -ne "Denied")) ' \
                      '{start-sleep -milliseconds 100}; ' \
                      '$acc = %d; ' \
                      'while($loc.position.location.horizontalaccuracy -gt $acc) ' \
                      '{start-sleep -milliseconds 100; $acc = [math]::Round($acc*1.5)}; ' \
                      '$loc.position.location.latitude; ' \
                      '$loc.position.location.longitude; ' \
                      '$loc.position.location.horizontalaccuracy; ' \
                      '$loc.stop()' % (accuracy))

    p = sp.Popen(pshellcomm, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
    (out, err) = p.communicate()
    out = re.split('\n', out)

    latitude = float(out[0])
    longitude = float(out[1])
    # print(latitude, longitude)
    return latitude, longitude

client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

temp = 30
humi = 50
light_intesity = 100
counter = 0

longitude = 0.0
latitude = 0.0
while True:
    # latitude, longitude = get_location()
    # print(latitude, longitude)
    # collect_data = {'temperature': temp, 'humidity': humi, 'light':light_intesity,
    #                 'longitude': longitude, 'latitude': latitude}
    # temp += 1
    # humi += 1
    # light_intesity += 1
    # client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    # time.sleep(10)
    if len(bbc_port) > 0:
        readSerial()
    time.sleep(1)