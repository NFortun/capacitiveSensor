#!/usr/bin/env python3
import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from prometheus_client import Gauge, start_http_server
import time
import sys
import os
import json
import paho.mqtt.client as mqtt
class MoistureSensor:
    DRY = 16800
    WET = 4600
    def __init__(self, name):
        ads = ADS.ADS1115(i2c)
        chan = AnalogIn(ads, ADS.P0)
        self.name = name
        self.chan = chan
    def ComputeMoist(self):
        moist = round(100 - ((self.chan.value / self.DRY )*100), 1)
        return moist
    def Name(self):
        return self.name
    def RawValue(self):
        return self.chan.value
    def RawVoltage(self):
        return self.chan.voltage

class PrometheusExporter:
    moistureGauge = Gauge("Moisture", "Percent of humidity of the soil",  ["name"])
    rawGauge = Gauge("Raw", "raw value of sensor", ["name"])
    voltageGauge = Gauge("Voltage", "Voltage of sensor", ["name"])
    def __init__(self,port=8080):
        start_http_server(port)

    def send(self, gauge, labels, value):
        gauge.labels(labels).set(value)
    def SendMetrics(self, name, moist, rawVoltage, rawValue):
        self.send(self.moistureGauge, name, moist)
        self.send(self.voltageGauge, name, rawVoltage)
        self.send(self.rawGauge, name, rawValue)

class MQTTExporter:
    client = mqtt.Client()
    def __init__(self):
        addr = os.getenv("MQTT_ADDR")
        port = os.getenv("MQTT_PORT")
        #access_token = os.getenv(ACCESS_TOKEN)
        #self.client.username_pw_set(ACESS_TOKEN)
        self.client.connect(addr, int(port), 60)
        self.client.loop_start()
    def Send(self, channel, data):
        self.client.publish(channel, data, 1)
        

if __name__ == '__main__':
    sensor = MoistureSensor("bonsai")
    moisture = {'moisture': 0}
    name = sensor.Name()
    prom = PrometheusExporter()
    mqttexporter = MQTTExporter()
    while True:
        moist = sensor.ComputeMoist()
        rawValue = sensor.RawValue()
        rawVoltage = sensor.RawVoltage()
        prom.SendMetrics(name, moist, rawVoltage, rawValue)
        moisture['moisture'] = moist
        mqttexporter.Send("moisture", json.dumps(moisture))
        print(rawValue, moist)
        sys.stdout.flush()
        time.sleep(1)
