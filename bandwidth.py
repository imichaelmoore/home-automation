""" Gets current bandwidth statistics from PfSense for each WAN connection, writes to Influx """
import time
from easysnmp import Session
from pprint import pprint
from influxdb import InfluxDBClient
import os

# Create an SNMP session to be used for all our requests
session = Session(hostname=os.getenv("PFSENSE_HOSTNAME"), community=os.getenv("PFSENSE_SNMP_COMMUNITY"), version=2)

client = InfluxDBClient(os.getenv("INFLUX_HOSTNAME"), 8086, os.getenv("INFLUX_USERNAME"), os.getenv("INFLUX_PASSWORD"), os.getenv("INFLUX_DATABASE"))

while True:

    json_body = [
                    {
                    "measurement": "fiber",
                    "fields": {
                        "in": float(session.get ('.1.3.6.1.2.1.2.2.1.10.2').value),
                        "out": float(session.get('.1.3.6.1.2.1.2.2.1.16.2').value),
                        }
                    },
                    {
                    "measurement": "starlink",
                    "fields": {
                        "in": float(session.get ('.1.3.6.1.2.1.2.2.1.10.3').value),
                        "out": float(session.get('.1.3.6.1.2.1.2.2.1.16.3').value),
                        }
                    },
                ]

    client.write_points(json_body)
    pprint(json_body)
    time.sleep(1)
