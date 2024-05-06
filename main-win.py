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
# Graphing the data
import matplotlib.pyplot as plt
import math

point_of_interest = 1.175e7  # Timestamp in ms that we are interested in
interest_radius = 1000 * 60 * .5  # How many ms before and after the point of interest to keep

drogue_deploy_time = 1.1763e7  # Timestamp in ms that we are interested in
launch_time = 1.1738e7
burnout_time = 1.1742e7

def decode_serial_file(file_path):
    total_measurement_bytes_collected = 0
    all_data = {}
    with open(file_path, 'rb') as f:
        lines = f.read().split(b"\0\r\n")
        for line in lines:
            # print(line)
            if len(line) != 12:
                print("bad length: ", len(line))
                print(f"Invalid line: {line}")
                continue
            data = struct.unpack("4sIf", line)
            total_measurement_bytes_collected += 4
            # print(f"data name: {data[0].decode()} timestamp: {data[1]}"
            #       f" data: {data[2]}")

            name = data[0].decode()
            # Remove the null character
            name = name.replace("\x00", "")
            measurement = data[2]
            timestamp = data[1]
            # if timestamp < point_of_interest - interest_radius:
            #     continue
            # if timestamp > point_of_interest + interest_radius:
            #     continue

            if timestamp not in all_data:
                all_data[timestamp] = {}
            all_data[timestamp][name] = measurement

    print(f"Total bytes of measured data collected: {total_measurement_bytes_collected}")

    return all_data


def save_data_to_csv(data):
    with open("data.csv", "w") as f:
        f.write("timestamp (ms),xac (m/s^2),yac (m/s^2),zac (m/s^2),xgy,ygy,zgy,tmp (C)\n")
        for timestamp, measurements in data.items():
            # print(timestamp, measurements)
            f.write(f"{timestamp},")
            f.write(f"{measurements.get('xac', 0)},")
            f.write(f"{measurements.get('yac', 0)},")
            f.write(f"{measurements.get('zac', 0)},")
            f.write(f"{measurements.get('xgy', 0)},")
            f.write(f"{measurements.get('ygy', 0)},")
            f.write(f"{measurements.get('zgy', 0)},")
            f.write(f"{measurements.get('tmp', 0)},")
            f.write("\n")


def plot_total_acl(data):
    acl_x = []
    acl_y = []
    acl_z = []
    acl_tot = []
    timestamps = []
    temperature = []
    for timestamp, measurements in data.items():
        acl_x.append(measurements.get('xac', 0))
        acl_y.append(measurements.get('yac', 0))
        acl_z.append(measurements.get('zac', 0))
        acl_tot.append(math.sqrt(measurements.get('xac', 0) ** 2 +
                                measurements.get('yac', 0) ** 2 +
                                measurements.get('zac', 0) ** 2))
        timestamps.append(timestamp / 1000)

    plt.plot(timestamps, acl_tot, label="Total Acceleration (m/s^2)")
    # plt.plot(timestamps, acl_x, label="X Acceleration (m/s^2)")
    # plt.plot(timestamps, acl_y, label="Y Acceleration (m/s^2)")
    # plt.plot(timestamps, acl_z, label="Z Acceleration (m/s^2)")

    # Make the lines thinner
    plt.setp(plt.gca().lines, linewidth=0.5)

    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration")

    # Disable scientific notation
    plt.ticklabel_format(style='plain')



    plt.legend()
    plt.show()


if __name__ == "__main__":
    data = decode_serial_file("LOG00029.TXT")
    plot_total_acl(data)
    # save_data_to_csv(data)

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
