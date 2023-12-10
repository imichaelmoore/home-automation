import os
import time
from typing import List, Dict
from easysnmp import Session
from influxdb import InfluxDBClient


def get_bandwidth_statistics(session: Session, if_index: int) -> Dict[str, float]:
    """
    Get bandwidth statistics for a given interface index.

    Args:
    session (Session): The SNMP session object.
    if_index (int): The interface index.

    Returns:
    Dict[str, float]: A dictionary containing inbound and outbound bandwidth.
    """
    in_oid = f".1.3.6.1.2.1.2.2.1.10.{if_index}"
    out_oid = f".1.3.6.1.2.1.2.2.1.16.{if_index}"
    return {
        "in": float(session.get(in_oid).value),
        "out": float(session.get(out_oid).value),
    }


def create_influxdb_session() -> InfluxDBClient:
    """
    Create an InfluxDB client session.

    Returns:
    InfluxDBClient: The InfluxDB client session.
    """
    return InfluxDBClient(
        os.getenv("INFLUX_HOSTNAME"),
        8086,
        os.getenv("INFLUX_USERNAME"),
        os.getenv("INFLUX_PASSWORD"),
        os.getenv("INFLUX_DATABASE"),
    )


def main():
    session = Session(
        hostname=os.getenv("PFSENSE_HOSTNAME"),
        community=os.getenv("PFSENSE_SNMP_COMMUNITY"),
        version=2,
    )

    client = create_influxdb_session()

    while True:
        json_body: List[Dict] = [
            {"measurement": "fiber", "fields": get_bandwidth_statistics(session, 2)},
            {"measurement": "starlink", "fields": get_bandwidth_statistics(session, 3)},
        ]

        client.write_points(json_body)
        print(json_body)
        time.sleep(1)


if __name__ == "__main__":
    main()
