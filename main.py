"""

struct SerialData{
    char name [4]; // 3 chars for name and 1 for null
    uint32_t timestamp_ms;
    float data;
};


void dataToSDCardSerial(String name, uint32_t timestamp_ms, float data, HardwareSerial &SD_serial){
    // Pack the data together
    struct SerialData theData = {"", timestamp_ms, data};
    strncpy(theData.name, name.c_str(), 3);
    theData.name[3] = '\0';
    SD_serial.write((uint8_t *) &theData, sizeof(theData));
    char dlim [2] = {'\0', '\n'};
    SD_serial.write((uint8_t *) &dlim, sizeof(dlim));

}


Data has been saved to a file using the above format, now I want to
decode the data back to its original form, and it's contents
"""

import struct
import pandas as pd


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

    with open(file_path, 'rb') as f:
        lines = f.read().split(b"\0\r\n")
        for line in lines:
            line = line.strip()
            if len(line) != 12:
                print("bad length: ", len(line))
                print(f"Invalid line: {line}")
                continue
            data = struct.unpack("4sIf", line)
            timestamp = data[1]
            if timestamp > oldest_timestamp:
                oldest_timestamp = timestamp
            if timestamp < youngest_timestamp:
                youngest_timestamp = timestamp

            name = data[0][:3].decode()
            measurement = data[2]

            all_data.add(name, timestamp, measurement)

            if name == "sta":
                print(data)

            if name == "xac":
                number_of_xac += 1

            bytes_of_good_data += 8
            bytes_of_measurements += 4
            bytes_of_data += 14

            print(f"data name: {name} timestamp: {timestamp}"
                  f" data: {measurement}")

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
    decode_serial_file("LOG00029.TXT")

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