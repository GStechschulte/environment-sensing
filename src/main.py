import configparser
from datetime import datetime
import time

import psycopg2
from psycopg2.extras import execute_values

from sensor import BME280


def connect_to_db(config):
    return psycopg2.connect(
        host=config["database"]["host"],
        port=config["database"]["port"],
        database=config["database"]["database"],
        user=config["database"]["user"],
        password=config["database"]["password"]
    )


def main():

    config = configparser.ConfigParser()
    config.read('config.ini')
    conn = connect_to_db(config)
    
    sensor = BME280()

    while True:
        time.sleep(1)
        try:
            pressure, temperature, humidity = sensor.read_data()
            # print(f"{datetime.utcnow()}, p: {pressure:.2f}, temp: {temperature:.2f}, hum: {humidity:.2f} %")
            with conn.cursor() as cur:
                execute_values(cur, """
                    INSERT INTO bosche_sensor (time, metric, value)
                    VALUES %s
                """, [(datetime.utcnow(), "temperature", temperature)])
                conn.commit()
        except KeyboardInterrupt:
            break



if __name__ == '__main__':
    main()