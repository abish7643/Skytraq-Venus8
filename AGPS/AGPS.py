import time
from ftplib import FTP
import serial
import serial.tools.list_ports


def ftp_download():
    print("connecting to FTP")
    with FTP('60.250.205.31') as ftp:
        print("FTP connected")
        ftp.login('skytraq', 'skytraq')
        print("FTP logged in")

        ftp.cwd('ephemeris')
        print("cd done")

        eph_data = bytearray()
        ftp.retrbinary('RETR Eph_4.dat', eph_data.extend)
        print("downloaded data")

        with open('Eph_4_Rom.dat', 'wb') as f:
            f.write(eph_data)
            print("file written")

        return eph_data


def device_port():
    ports = serial.tools.list_ports.comports()
    device_ports = []

    for port, desc, hwid in sorted(ports):
        # print("{}: {} [{}]".format(port, desc, hwid))
        if "USB to UART" in desc:
            device_ports.append(port)

    return device_ports


def split_file(file_bytearray):
    bytearray_length = len(file_bytearray)
    bytearray_split_length = bytearray_length / 94

    print("File size: {} bytes, Number of 94 byte chunks: {}".format(bytearray_length, bytearray_split_length))

    split_bytearray = []

    for i in range(0, int(bytearray_split_length)):
        split_bytearray.append(file_bytearray[(i * 94):((i + 1) * 94)])

    return split_bytearray


eph_data = ftp_download()

device_port = device_port()[0]
print("Using {}".format(device_port))
receiver = serial.Serial(port=device_port, baudrate=115200)

file = open("Eph_4_Rom.dat", "rb")
file_bytearray = file.read()
split_bytearray = split_file(file_bytearray)

print(file_bytearray)
print(split_bytearray)
print(len(split_bytearray))


# for j in split_bytearray:
#     receiver.write(j)
#     time.sleep(0.05)
#     read_data = receiver.read_all()
#     print(read_data)

# receiver.write(split_bytearray[0])
# while True:
#     read_data = receiver.readline()
#     print(read_data)


j = 0
receiver.write(split_bytearray[j])
ack = b'\xa1'

while True:
    read_data = receiver.readline()

    if ack in read_data:
        print(read_data)
        j = j + 1

        if j < len(split_bytearray):
            print(j)
            receiver.write(split_bytearray[j])
        else:
            break
