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
    config.read('../config.ini')
    conn = connect_to_db(config)
    
    sensor = BME280()

    print("DB and connection to sensor successful...")
    print("Sensor is read every 60 seconds...")
    while True:
        try:
            pressure, temperature, humidity = sensor.read_data()
            with conn.cursor() as cur:
                execute_values(cur, """
                    INSERT INTO bosche_sensor (time, metric, value)
                    VALUES %s
                """, [(datetime.utcnow(), "temperature", temperature)])
                conn.commit()
                print(f"Data inserted successfully - Time: {datetime.utcnow()}, Temperature: {temperature:.2f} °C")
            time.sleep(60)
        except KeyboardInterrupt:
            break
        

if __name__ == '__main__':
    main()