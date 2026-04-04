"""
Purpose.......: NIBE DVC 10 python command and control script
HW Infon......: https://www.nibe.eu/sv-se/produkter/ventilation/dvc-10
Tested HW.....: OEM version 2.0.1 sold by NIBE, OEM manufactured by VENTS
Usage.........: Home Assistant or from commandline as function with python3
github source.: https://github.com/danielolsson100
License.......: GNU General Public License 3 as published by the Free Software Foundation
Protocol......: UDP
Port..........: 4000
Created by....: @danielolsson100
Notes.........: No API doc is not available from vendor, the code is done by reverse engineering the network traffic to the device to figure out how to control it by levering WireShark and Packet Sender.
"""

import sys
import socket

if len(sys.argv)<3:
    print("Fatal....: You missed to add all arguments as input!")
    print("Usage....: python", sys.argv[0],  "IP ADDRESS COMMAND")
    print("Example..: python", sys.argv[0], "192.168.1.20 start")
    print("COMMANDs.: start, stop, mode-day, mode-night, fan-speed-low, fan-speed-medium, fan-speed-high, airflow-oneway, airflow-twoway, airflow-in")
    sys.exit(1)

""" HEX reference
Base sendhex 6d6f62696c65     mobile
Base returnhex 6D6173746572   master
Get Status                    01 0d
Get/Set if the device is ON   03 0d
Get/Set Fan Speed, 1,2,3      LOW:04 01   / Medium:04 02  / High:04 03
Get/Set Mode                  AUTO:06 00  / OUT:06 01     / IN:06 02 
Get/Set Night Mode            09 01

UPD datagram response 
Example IP 192.168.1.20 Port 4000 UDP with Packet Sender 
Send: 6d 6f 62 69 6c 65 01 0d
Resp: 6D 61 73 74 65 72 03 01 09 00 0C 00 13 00 0D 00 1A 00 04 01 05 16 06 01 08 32 0E 00 00 00 12 00 14 00 25 00 

Response array data definition
data[6]:  03   - Operation Status
data[7]:  01=ON / 00=OFF
data[8]:  t/09 - Mode Status
data[9]:  00=Mode Day / 01=Mode Night / 02=Mode Party
data[10]: 0c   - Undefined
data[11]: 00   - Undefined
data[12]: 13   - Undefined
data[13]: 00   - Undefined
data[14]: r/14 - Undefined
data[15]: 00   - Undefined
data[16]: 1a   - Undefined
data[17]: 00   - Undefined
data[18]: 04   - Fan Status
data[19]: 01=Low / 02=Medium / 03=High / 04=Manual Speed enabled
data[20]: 05 - Manual Fan Speed
data[21]: 00=9% ... ff=100%
data[22]: 06   - Airflow Mode
data[23]: 00=Mode[-->|-->] / 01=Mode[<--|-->] / 02=Mode[-->|<--]
data[24]: 08   - Undefined
data[25]: 32   - Undefined
data[26]: 0E   - Undefined
data[27]: 00   - Undefined
data[28]: 00   - Undefined
data[29]: 00   - Undefined
data[30]: 12   - Undefined
data[31]: 00   - Undefined
data[32]: 14   - Undefined
data[33]: 00   - Undefined
data[34]: 25   - Undefined
data[35]: 00   - Undefined
"""

# args
ip = str(sys.argv[1])
requested_state = str(sys.argv[2])

# static HEX values
base_send_hex = '6d6f62696c65'
get_data_hex = '010d'
set_onoff_hex = '030d'
set_fan_speed_low_hex = '0401'
set_fan_speed_medium_hex = '0402'
set_fan_speed_high_hex = '0403'
set_airflow_oneway_hex = '0600'
set_airflow_twoway_hex = '0601'
set_airflow_in_hex = '0602'
set_daynight_hex = '0901'
# static INT values
datagram_size = 4096
port = 4000
datagram_timeout_sec = 1
# dynamic values
server_address = (ip, port)

# functions
def send_udp_dgr(hex_val, server_address):
    sock.sendto(bytes.fromhex(hex_val), server_address)
    data, address = sock.recvfrom(datagram_size)   
    if data is None:
        print("No data was received from ", address, "\n")
    else:
        return data

# main 
# Initiate UDP socket for sendning data
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(datagram_timeout_sec)

# Get status if the device
data = send_udp_dgr((base_send_hex+get_data_hex), server_address)
#print("Data before: " ,data,)

# if block to compare data bits and set values if needed
if requested_state == 'start':
    if data[7] != 1:
       data = send_udp_dgr((base_send_hex+set_onoff_hex), server_address)
elif requested_state == 'stop':
    if data[7] != 0:
        data = send_udp_dgr((base_send_hex+set_onoff_hex), server_address)

elif requested_state == 'mode-day':
    if data[9] != 0:
       data = send_udp_dgr((base_send_hex+set_daynight_hex), server_address)
elif requested_state == 'mode-night':
    if data[9] != 1:
        data = send_udp_dgr((base_send_hex+set_daynight_hex), server_address)

elif requested_state == 'fan-speed-low':
    if data[19] != 1:
       data = send_udp_dgr((base_send_hex+set_fan_speed_low_hex), server_address)
elif requested_state == 'fan-speed-medium':
    if data[19] != 2:
        data = send_udp_dgr((base_send_hex+set_fan_speed_medium_hex), server_address)
elif requested_state == 'fan-speed-high':
    if data[19] != 3:
        data = send_udp_dgr((base_send_hex+set_fan_speed_high_hex), server_address)

elif requested_state == 'airflow-oneway':
    if data[23] != 0:
       data = send_udp_dgr((base_send_hex+set_airflow_oneway_hex), server_address)
elif requested_state == 'airflow-twoway':
    if data[23] != 1:
        data = send_udp_dgr((base_send_hex+set_airflow_twoway_hex), server_address)
elif requested_state == 'airflow-in':
    if data[23] != 2:
        data = send_udp_dgr((base_send_hex+set_airflow_in_hex), server_address)
else:
    print("Undefined COMMAND")

#print("Data after.: " ,data, "\n")
sock.close()
