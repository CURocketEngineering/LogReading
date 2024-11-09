

import struct
import pandas as pd
from enum import Enum

class DataNames(Enum):
    ACCELEROMETER_X = 0
    ACCELEROMETER_Y = 1
    ACCELEROMETER_Z = 2
    GYROSCOPE_X = 3
    GYROSCOPE_Y = 4
    GYROSCOPE_Z = 5
    TEMPERATURE = 6
    PRESSURE = 7
    ALTITUDE = 8
    MAGNETOMETER_X = 9
    MAGNETOMETER_Y = 10
    MAGNETOMETER_Z = 11
    MEDIAN_ACCELERATION_SQUARED = 12
    AVERAGE_CYCLE_RATE = 13

    def __str__(self):
        return self.name.lower()

class AllData:
    def __init__(self):
        self.data = {}  # Time stamp: data dict pairs

    def add(self, name, timestamp, data):
        if "ac" not in name:
            return
        if timestamp not in self.data:
            self.data[timestamp] = {}
        self.data[timestamp][name] = data

        # If all three accelerometer data is present for this timestamp,
        # then calculate the magnitude of the acceleration
        if len(self.data[timestamp]) == 3:
            x = self.data[timestamp]["xac"]
            y = self.data[timestamp]["yac"]
            z = self.data[timestamp]["zac"]
            self.data[timestamp]["mag"] = (x**2 + y**2 + z**2)**0.5


def decode_serial_file(file_path):
    youngest_timestamp = float("inf")
    oldest_timestamp = 0
    bytes_of_measurements = 0
    bytes_of_good_data = 0
    bytes_of_data = 0

    number_of_xac = 0

    all_data = AllData()

    temp_out = open("temp.txt", "w")

    # headers
    temp_out.write(f"{'Data Name':<30} {'Timestamp':<15} {'Data':<10}\n")

    with open(file_path, 'rb') as f:
        lines = f.read().split(b"\0\r\n")
        for line in lines:
            if len(line) != 9:
                print("bad length: ", len(line))
                print(f"Invalid line: {line}")
                continue
            data = struct.unpack("IfB", line)
            timestamp = data[0]
            measurement = data[1]
            name = data[2]

            if timestamp > oldest_timestamp:
                oldest_timestamp = timestamp
            if timestamp < youngest_timestamp:
                youngest_timestamp = timestamp

            # all_data.add(name, timestamp, measurement)

            

            if name == DataNames.ACCELEROMETER_X.value:
                number_of_xac += 1

            bytes_of_good_data += 8
            bytes_of_measurements += 4
            bytes_of_data += 14

            print(f"data name: {DataNames(name)} timestamp: {timestamp}"
                  f" data: {measurement}")
            temp_out.write(f"{DataNames(name):<30} {timestamp:<15} {measurement:<10}\n")

    print(f"youngest timestamp: {youngest_timestamp}")
    print(f"oldest timestamp: {oldest_timestamp}")
    print(f"bytes of measurements: {bytes_of_measurements}")
    print(f"bytes of good data: {bytes_of_good_data}")
    print(f"total bytes: {bytes_of_data}")

    seconds_elapsed = (oldest_timestamp - youngest_timestamp) / 1000
    print("Sensor entries per second:", len(lines) / seconds_elapsed)

    print("Number of xac entries:", number_of_xac)
    print("Number of xac entries per second:", number_of_xac / seconds_elapsed)

    measurement_data_per_second = bytes_of_measurements / seconds_elapsed
    print("------Data Rates (Bytes)---------")
    print(f"actual measurement data per second: {measurement_data_per_second}")
    print(
        f"good data (measurements + timestamps) per second: {bytes_of_good_data / seconds_elapsed}")
    print(
        f"total data per second (measurements + timestamps + names + deliminators): {bytes_of_data / seconds_elapsed}")


    # Save all_data as a csv
    # df = pd.DataFrame(all_data.data)
    # df.to_csv("all_data.csv")


if __name__ == "__main__":
    decode_serial_file("LOG00060.TXT")

"""
Expected:
data name: alt--data timestamp: 6201
data name: xac--data timestamp: 0
data name: yac--data timestamp: 0
data name: zac--data timestamp: 9
data name: xgy--data timestamp: 0
data name: ygy--data timestamp: 0
data name: zgy--data timestamp: 0
data name: tmp--data timestamp: 27
data name: prs--data timestamp: 460
data name: alt--data timestamp: 6227
data name: xac--data timestamp: 0
data name: yac--data timestamp: 0
data name: zac--data timestamp: 10
data name: xgy--data timestamp: 0
data name: ygy--data timestamp: 0
data name: zgy--data timestamp: 0
data name: tmp--data timestamp: 27
data name: prs--data timestamp: 458
data name: alt--data timestamp: 6231
data name: xac--data timestamp: 0
data name: yac--data timestamp: 0
data name: zac--data timestamp: 10
data name: xgy--data timestamp: 0
data name: ygy--data timestamp: 0
data name: zgy--data timestamp: 0
data name: tmp--data timestamp: 27
data name: prs--data timestamp: 459

"""