"""
    Read and save data from the SparkFun Triad Spectroscopy Sensor
    by
    Szymon Jakubiak
    Twitter: @SzymonJakubiak
    LinkedIn: https://www.linkedin.com/in/szymon-jakubiak-495442127/
"""

import serial, time
from datetime import datetime

# Specify serial port
device_port = "COM194"

# Specify output file name, comment and header for data
output_file = "SL_spectrp.txt"
comment = "Comment"
data_header = "date,time,410,435,460,485,510,535,560,585,610,645,680,705,730,760,810,860,900,940" # Separate data columns by commas
data_units = "yyyy.mm.dd,hh:mm:ss:msmsms,nm,nm,nm,nm,nm,nm,nm,nm,nm,nm,nm,nm,nm,nm,nm,nm,nm,nm" # Separate data columns by commas

# Create object for serial port
device_ser = serial.Serial(device_port, baudrate=9600, stopbits=1, parity="N",  timeout=2)
device_ser.flushInput()

# Create data buffer and specify number of consecutive
# measurements to buffer before writing to the file
output_buffer = ""
buffer_len = 60

def quality_check(data):
    """
    Expects string, returns tuple with valid data
    or False when data was invalid
    """
    valid = len(data.split(",")) == 18
    
    if data != False and valid:
        return data

    else:
        return False

def ser_data(ser):
    """
    Expects serial port object as an input, returns data from serial device
    or False when there was no data to read
    """
    # Wait for the begginning of the message
    if ser.inWaiting() > 0:
        data = b""
        last_byte = b""
        # Loop untill the end character was read
        while last_byte != b"\xff":
            last_byte = ser.read()
            data += last_byte
        data = data[:-1].decode().rstrip()
        return quality_check(data)
    else:
        return False

def time_stamp():
    """
    Expects nothing, returns time stamp in format dd:mm:yyyy,hh:mm:ss:msmsms
    """
    date = datetime.now()
    stamp = "{0:4}.{1:02}.{2:02},{3:02}:{4:02}:{5:02}:{6:03.0f}".format(date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond / 1000)
    return stamp

def buffer_to_file(filename, data):
    """
    Expects two strings: filename and data which will be written to the file
    """
    file = open(filename, "a")
    file.write(data)
    file.close()

header = "\n* * * *\n" + comment + "\n* * * *\n"
header += data_header + "\n" + data_units
#print(header)
file = open(output_file, "a")
file.write(header + "\n")
file.close()

try:
    while True:
        output = ser_data(device_ser)
        if output != False:
            formatted_output = time_stamp() + "," + output
            #print(formatted_output)
            output_buffer += formatted_output + "\n"
            if output_buffer.count("\n") > buffer_len:
                buffer_to_file(output_file, output_buffer)
                output_buffer = ""
        else:
            time.sleep(0.001)

except KeyboardInterrupt:
    device_ser.close()
    buffer_to_file(output_file, output_buffer)
    print("Data logging stopped")

