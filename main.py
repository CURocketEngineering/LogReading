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

def decode_serial_file(file_path):
    with open(file_path, 'rb') as f:
        lines = f.read().split(b"\0\r\n")
        for line in lines:
            # print(line)
            if len(line) != 12:
                print("bad length: ", len(line))
                print(f"Invalid line: {line}")
                continue
            data = struct.unpack("4sIf", line)
            print(f"data name: {data[0].decode()} timestamp: {data[1]}"
                  f" data: {data[2]}")


if __name__ == "__main__":
    decode_serial_file("LOG00015.TXT")



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

