from sensor import BME280
import time


if __name__ == '__main__':
    sensor = BME280()
    
    while True:
        time.sleep(1)
        try:
            pressure, temperature, humidity = sensor.read_data()
            print(f"p: {pressure:.2f}, temp: {temperature:.2f}, hum: {humidity:.2f} %")
        except KeyboardInterrupt:
            break