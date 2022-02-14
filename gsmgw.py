#!/usr/bin/python3

import socket
from urllib.parse import unquote
import random
import datetime

# Definitions for API connect
HOST = 'ip'
PORT = port
LOGIN = 'login'
PASS = 'passowrd'


PAYLOAD = 'Action: Login\r\nUsername: ' + LOGIN + '\r\nSecret: ' + PASS + '\r\n\r\n'
logs_file = "/home/ro/Desktop/GSMTST/gsmapi.log" 

def to_bytes(s):
     if type(s) is bytes:
         return s
     elif type(s) is str or (sys.version_info[0] < 3 and type(s) is unicode):
         return codecs.encode(s, 'utf-8')
     else:
         raise TypeError("Expected bytes or string, but got %s." % type(s))

def file_path_get(span):
    # You can change file path for SMS - every GSMGW span have own file.
    if span == 2:
        return("/home/ro/Desktop/GSMTST/1/")
    elif span == 3:
        return("/home/ro/Desktop/GSMTST/2/")
    elif span == 4:
        return("/home/ro/Desktop/GSMTST/3/")
    elif span == 5:
        return("/home/ro/Desktop/GSMTST/3/")



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall(PAYLOAD.encode('utf-8'))
data_ACM = s.recv(1024)
data_RESPONSE_AUTH = s.recv(1024)
with open(logs_file, 'a') as file:
        file.write("[" + str(datetime.datetime.now()) + "]" + "Starting GSM API service\n")
        file.write("[" + str(datetime.datetime.now()) + "]" + str(data_RESPONSE_AUTH) + "\n")

while True:

    data_RESPONSE = s.recv(1024)
    data_BYTES = to_bytes(data_RESPONSE) 
    data = str(data_BYTES)
    data_PARSED = data.split('\\r\\n')
    data_GSMSPAN = int((data_PARSED[3][9:]))
    


    data_NUMBER = (data_PARSED[4][8:])
    data_MESSAGE = (data_PARSED[9][9:])
    data_MESSAGE_E = unquote(data_MESSAGE).replace("+", " ")[1:]
    RANDOM_ID = random.randint(1000,9000)
    file_path = str(file_path_get(data_GSMSPAN)) + str(data_NUMBER) + str(RANDOM_ID) + ".txt"
    with open(file_path, 'a') as file:
        file.write("From: " + "00" + str(data_NUMBER)[1:] + "\n")
        file.write(str(data_MESSAGE_E) + "\n")
    with open(logs_file, 'a') as file:
        file.write("[" + str(datetime.datetime.now()) + "]" + "Recieve SMS from-" + str(data_NUMBER)[1:] + " with content-" + str(data_MESSAGE_E) + "\n")

    print ('From:', repr(data_NUMBER), repr(data_MESSAGE_E))
   

    
