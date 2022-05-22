#!/usr/bin/env python3
import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from prometheus_client import Gauge, start_http_server
import time
import sys

class MoistureSensor:
    DRY = 16800
    WET = 4600
    def __init__(self, name):
        ads = ADS.ADS1115(i2c)
        chan = AnalogIn(ads, ADS.P0)
        self.name = name
        self.chan = chan
    def ComputeMoist(self):
        moist = 100 - ((self.chan.value) / self.DRY )*100
        return moist
    def Name(self):
        return self.name
    def RawValue(self):
        return self.chan.value
    def RawVoltage(self):
        return self.chan.voltage

if __name__ == '__main__':
    start_http_server(8000)
    sensor = MoistureSensor("bonsai")
    g = Gauge("Moisture", "Percent of humidity of the soil",  ["name"])
    rawGauge = Gauge("Raw", "raw value of sensor", ["name"])
    voltageGauge = Gauge("Voltage", "Voltage of sensor", ["name"])
    while True:
        moist = sensor.ComputeMoist()
        g.labels(sensor.Name()).set(moist)
        rawGauge.labels(sensor.Name()).set(sensor.RawValue())
        print(sensor.RawValue(), moist)
        sys.stdout.flush()
        voltageGauge.labels(sensor.Name()).set(sensor.RawVoltage())
        time.sleep(3600)
