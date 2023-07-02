import os
import sys
import ctypes
import random
import json
from Crypto.PublicKey import RSA
import bson
import myMessage
import requests
import time
from PIL import Image
from io import BytesIO
import base64
import threading
import socket, sys
import mdatabases



class Server:
    def __init__(self, HOST, PORT):
        self.host = HOST
        self.port = PORT
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(1)
        self.collection = mdatabases.get_collection()
        self.device_sockets = dict()
        print("server running...")

    def accept(self) -> tuple[socket.socket, tuple] :
        client_socket, client_address = self.server_socket.accept()
        print('client connect', client_address)
        return client_socket, client_address
    
    def exit(self):
        self.server_socket.close()
    
    def createThread(self, client_socket, client_address):
        thread = threading.Thread(target=self.threadWork,args=(client_socket,client_address))   # 設定線程
        return thread

    def messageForward(self, msg: myMessage.myMessage ):
        print(msg)
        device = msg.getSourceDevice()
        if device == myMessage.DeviceType.device:
            self.messageForward_device2client(msg)
        elif device == myMessage.DeviceType.client:
            self.messageForward_client2device(msg)

    # 再考慮要不要更新msg的source
    def messageForward_device2client(self, msg: myMessage.myMessage ):
        device_id = msg.getSourceDeviceId()
        client_ids = mdatabases.getBindClientFromDeviceId(self.collection, device_id)
        for c in filter(lambda c : c in self.device_sockets, client_ids):
            self.sendMessage(msg)     
    
    def messageForward_client2device(self, msg: myMessage.myMessage ):
        device_id = msg.getSourceDeviceId()
        if(device_id not in self.device_sockets):
            print("device [%s] offline" % device_id)
        else:
            print(device_id)
            self.sendMessage(msg) 
        
    def sendMessage(self, msg: myMessage.myMessage ):
        self.device_sockets[msg.getTargetDeviceId()].sendall(str(msg).encode(encoding='utf_8', errors='strict'))
        
        
    def createMessage_changeBackground(self, device_id, **parameters):
        return myMessage.myMessage({
            "targetDeviceId" : device_id,
            "targetDevice" : myMessage.DeviceType.device,
            "sourceDeviceId" : '',
            "sourceDevice" : myMessage.DeviceType.server,
            "action" : myMessage.ActionType.changeBackground,
            "parameters" : parameters
        })
    
    def sendMessageAction(self, Action, *arg, **kwarg):
        if Action == myMessage.ActionType.resultOnline:
            msg = myMessage.myMessage({
                "targetDeviceId" : kwarg['targetDeviceId'],
                "targetDevice" : kwarg['targetDevice'],
                "sourceDeviceId" : '',
                "sourceDevice" : myMessage.DeviceType.server,
                "action" : myMessage.ActionType.resultOnline,
                "parameters" : kwarg['parameters']
            })
            self.sendMessage(msg)
            print(msg)
        
        elif Action == myMessage.ActionType.ACK:
            msg = myMessage.myMessage({
                "targetDeviceId" : kwarg['targetDeviceId'],
                "targetDevice" : kwarg['targetDevice'],
                "sourceDeviceId" : '',
                "sourceDevice" : myMessage.DeviceType.server,
                "action" : Action,
                "parameters" : {}
            })
            # self.sendMessage(msg)
        pass

    def handleResponse(self, response: str):
        msg = myMessage.myMessage(response)
        device_id = msg.getSourceDeviceId()
        if msg.action == myMessage.ActionType.exit:
            self.device_sockets[device_id].close()
            self.device_sockets.pop(device_id, None)
        
        elif msg.action == myMessage.ActionType.online \
            and msg.getSourceDevice() == myMessage.DeviceType.device:
            
            mdatabases.setDeviceIdOnlineTime(self.collection, device_id, msg.parameters['last_time'])
            self.sendMessageAction(myMessage.ActionType.ACK, targetDeviceId=device_id,
                                   targetDevice=myMessage.DeviceType.device)
            # 12345
 
        elif msg.action == myMessage.ActionType.checkOnline \
            and msg.getSourceDevice() == myMessage.DeviceType.client:
            if 'device_ids' not in msg.parameters:
                print('"device_ids" not in msg.parameters')
                # TODO: 不確定須不須要回傳Response

            # TODO: check bind id

            sendParameters = {
                "result" : []
            }
            for d in msg.parameters['device_ids']:
                c = self.createResultOnlineParameterById( d)
                sendParameters['result'].append(c)
            
            self.sendMessageAction(myMessage.ActionType.resultOnline, targetDeviceId=device_id,
                                   targetDevice=myMessage.DeviceType.client, parameters=sendParameters)
            
        elif msg.action == myMessage.ActionType.changeBackground \
            and msg.getSourceDevice() == myMessage.DeviceType.client: # 這部分是透過轉發來完成的
            pass
    
    def createResultOnlineParameterById(self, device_id):
        last_time = mdatabases.getDeviceIdOnlineTime(self.collection, device_id)
        return { 'device_id': device_id, 'last_time' : last_time}

    def threadWork(self, client_socket: socket.socket, client_address: tuple):
        try:
            while True:
                response = myMessage.readResponse(client_socket)
                msg = myMessage.myMessage(response)
                print("get", msg.action, "from", msg.getSourceDeviceId())
                if not msg:
                    continue
                else:
                    device_id = msg.getSourceDeviceId()
                    if device_id not in self.device_sockets:
                        self.device_sockets[device_id] = client_socket
                    elif client_socket.getpeername() != self.device_sockets[device_id].getpeername():
                        self.device_sockets[device_id].close()
                        self.device_sockets[device_id] = client_socket
                        print("change socket")
                    
                if msg.getTargetDevice() != myMessage.DeviceType.server:
                    print("forward")
                    self.messageForward(msg)
                else:
                    self.handleResponse(response)
                    
        except: pass



HOST, PORT = '0.0.0.0', 12345
server = Server(HOST, PORT)
# server.createResultOnlineParameterById("112233")
while True:
    client_socket, client_address = server.accept()
    thread = server.createThread(client_socket, client_address)
    thread.start()
