#!/usr/bin/python3
#Python SMS sender and recivier for Yeastar GSM GW model TG400 - made by RK.

import socket
from urllib.parse import unquote
import random
import datetime
import os
import sched, time
from multiprocessing import Process
import urllib.parse
import requests


# Definitions for API connect
HOST = 'HOST'
PORT = PORT
LOGIN = 'LOGIN'
PASS = 'PASS'


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
        return("/home/ro/Desktop/GSMTST/1/IN/")
    elif span == 3:
        return("/home/ro/Desktop/GSMTST/2/IN/")
    elif span == 4:
        return("/home/ro/Desktop/GSMTST/3/IN/")
    elif span == 5:
        return("/home/ro/Desktop/GSMTST/4/IN/")


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall(PAYLOAD.encode('utf-8'))
data_ACM = s.recv(1024)
data_RESPONSE_AUTH = s.recv(1024)
with open(logs_file, 'a') as file:
    file.write("[" + str(datetime.datetime.now()) + "]" + "Starting GSM API service\n")
    file.write("[" + str(datetime.datetime.now()) + "]" + str(data_RESPONSE_AUTH) + "\n")

def recieve():
    while True:

        data_RESPONSE = s.recv(1024)
        data_BYTES = to_bytes(data_RESPONSE) 
        data = str(data_BYTES)
        data_PARSED = data.split('\\r\\n')
        print (data_PARSED)
        data_GSMSPAN = int((data_PARSED[3][9:]))
    
        data_NUMBER = (data_PARSED[4][8:])
        data_MESSAGE = (data_PARSED[9][9:])
        data_MESSAGE_E = unquote(data_MESSAGE).replace("+", " ")[1:]
        RANDOM_ID = random.randint(1000,9000)
        file_path = str(file_path_get(data_GSMSPAN)) + "IN" + str(data_NUMBER) + str(RANDOM_ID) + ".txt"
        with open(file_path, 'a') as file:
            file.write("From: " + "00" + str(data_NUMBER)[1:] + "\n")
            file.write(str(data_MESSAGE_E) + "\n")
        with open(logs_file, 'a') as file:
            file.write("[" + str(datetime.datetime.now()) + "]" + "Recieve SMS from-" + str(data_NUMBER)[1:] + " with content-" + str(data_MESSAGE_E) + "\n")

        print ('From:', repr(data_NUMBER), repr(data_MESSAGE_E))


def send():
        for filename in os.listdir('/home/ro/Desktop/GSMTST/2/OUT/'):
            if filename.endswith('.txt'):
                with open('/home/ro/Desktop/GSMTST/2/OUT/' + filename, 'r') as f:
                    lines = f.readlines()
                    TO_NUMBER = ("+" + lines[0][6:]).rstrip("\n")
                    TO_CONTENT = lines[5].rstrip("\n")
                    SPAN = (lines[3][12:]).rstrip("\n")
                    URL_ENCODED_MESSAGE = urllib.parse.quote(TO_CONTENT)
                    RANDOM_ID_S = random.randint(1000,9000)
                    SEND_PAYLOAD = str("http://" + HOST + ":88" + "/cgi/WebCGI?1500101=account=" + LOGIN + "&password="+ PASS +"&port="+ SPAN +"&destination="+ TO_NUMBER +"&content=" + URL_ENCODED_MESSAGE)
                    response = requests.get(SEND_PAYLOAD)
                    print(SEND_PAYLOAD)

                    os.replace("/home/ro/Desktop/GSMTST/"+ SPAN + "/OUT/" + filename, "/home/ro/Desktop/GSMTST/"+ SPAN +"/SENT/" + filename)

def sender():
    a = sched.scheduler(time.time, time.sleep)
    def file_exist_checker(sc): 
        print("Checking if file exist:")
        send()
        a.enter(5, 1, file_exist_checker, (sc,))
    a.enter(5, 1, file_exist_checker, (s,))
    a.run()

if __name__ == '__main__':
  p1 = Process(target=sender)
  p1.start()
  p2 = Process(target=recieve)
  p2.start()
  p1.join()
  p2.join()    

