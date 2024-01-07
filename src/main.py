import configparser
import time

from argparse import ArgumentParser
from datetime import datetime

from psycopg2.extras import execute_values
from sqlalchemy import create_engine

from sensor import BME280


def connect_to_db(config):
    
    host=config["pg"]["host"]
    port=config["pg"]["port"]
    database=config["pg"]["database"]
    user=config["pg"]["user"]
    password=config["pg"]["password"]
    
    db_url = f"postgresql://{user}:{password}@{host}/{database}"

    return create_engine(db_url)


def main(args):

    config = configparser.ConfigParser()
    config.read('../config.ini')
    conn = connect_to_db(config)
    
    sensor = BME280()
    print("Connection to sensor successful...")
    print("Sampling every 60 seconds...")

    if args.write_to_db:
        print("DB connection successful...")
    else:
        print("Not writing values to DB. Printing to console...")

    while True:
        try:
            pressure, temperature, humidity = sensor.read_data()
            if args.write_to_db:
                with conn.cursor() as cur:
                    execute_values(cur, """
                        INSERT INTO bosche_sensor (time, metric, value)
                        VALUES %s
                    """, [(datetime.now(), "temperature", temperature)])
                    conn.commit()
                    print(f"Data inserted successfully - Time: {datetime.now()}, Temperature: {temperature:.2f} °C")
            else:
                print(f"Time: {datetime.now()}, Temperature: {temperature:.2f} °C")
            print(f"Time: {datetime.now()}, Temperature: {temperature:.2f} °C")
            time.sleep(1)
        except KeyboardInterrupt:
            break
        

if __name__ == '__main__':
    parser = ArgumentParser(description="Bosche Sensor")
    parser.add_argument("--write_to_db", default=False, type=bool)
    args = parser.parse_args()
    main(args)
