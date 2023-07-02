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
import socket
import threading


class Client:
    
    def __init__(self):
        self.readData()
        pass

    def readData(self):
        self.path = os.path.abspath(os.path.dirname(sys.argv[0]))
        try:
            f = open(os.path.join(self.path, 'data.json'), 'r')
            dataJson = json.load(f)
            self.id = dataJson[0]["id"]
            self.public_key = dataJson[0]["public_key"]
            self.private_key = dataJson[0]["private_key"]

            f.close()

        except FileNotFoundError as err:
            f.close()
            self.initData()
        except json.decoder.JSONDecodeError as err:
            f.close()
            self.initData()

    def initData(self):
        self.id = self.createId()
        key = self.createRSAKey()
        self.public_key = key["public_key"]
        self.private_key = key["private_key"]
        self.saveData()


    def createId(self):
        return bson.ObjectId()
    
    def createRSAKey(length = 1024):
        key = RSA.generate(1024)

        # Extract private and public keys
        return {
            "private_key" : key.export_key(),
            "public_key" : key.publickey().export_key()
        }

    def saveData(self):
        data = [
            {
                "id" : str(self.id), 
                "private_key": self.private_key.decode("utf-8") , 
                "public_key": self.public_key.decode("utf-8") 
            }
        ]
        with open(os.path.join(self.path, 'data.json'), "w") as f:
            print(json.dumps(data, indent=4), file=f)

    # def receivedMessage(self, text):
    #     msg = myMessage.myMessage(text)
    #     if msg.action == myMessage.ActionType.changeBackground:
    #         self.changeBackground(msg)

    #     pass

    def changeBackground(self, msg: myMessage.myMessage):
        params = msg.getParameters()
        done = False

        if "url" in params:
            if self.getImageFromUrl(params["url"]) == "Error Image Url":
                pass
            else:
                done = True
            
        elif "base64" in params:
            if self.getImageFromBase64(params["base64"]) == "Error Image Url":
                pass
            else:
                done = True
        if not done:
            return
        image_path = os.path.join(self.path,"backage_image.jpg")
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)

        
    def getImageFromUrl(self, url):
        try:
            response = requests.get(url)
            image_data = response.content
            image = Image.open(BytesIO(image_data)).convert('RGB')

            temp_image_path = os.path.join(self.path ,"backage_image.jpg")
            image.save(temp_image_path, 'JPEG')
            image.close()
        except Exception as e:
            return "Error Image Url"

    def getImageFromBase64(self, image_base64):
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data)).convert('RGB')

                # Save the image to a temporary file
            temp_image_path = os.path.join(self.path,"backage_image.jpg")
            image.save(temp_image_path, 'JPEG')
            image.close()
        except:
            return "Error Image Base64"

    def sendMessageAction(self, Action, *arg, **kwarg):
        if Action == myMessage.ActionType.online:
            msg = myMessage.myMessage({
                "targetDeviceId" : "",
                "targetDevice" : myMessage.DeviceType.server,
                "sourceDeviceId" : self.id,
                "sourceDevice" : myMessage.DeviceType.device,
                "action" : myMessage.ActionType.online,
                "parameters" : {
                    "last_time" : str(int(time.time()))
                }
            })
            self.sendMessage(msg)
        elif Action == myMessage.ActionType.exit:
            msg = myMessage.myMessage({
                "targetDeviceId" : "",
                "targetDevice" : myMessage.DeviceType.server,
                "sourceDeviceId" : self.id,
                "sourceDevice" : myMessage.DeviceType.device,
                "action" : myMessage.ActionType.exit,
                "parameters" : {}
            })
            self.sendMessage(msg)
        elif Action == myMessage.ActionType.hello:
            msg = myMessage.myMessage({
                "targetDeviceId" : "",
                "targetDevice" : myMessage.DeviceType.server,
                "sourceDeviceId" : self.id,
                "sourceDevice" : myMessage.DeviceType.device,
                "action" : myMessage.ActionType.hello,
                "parameters" : {}
            })
            self.sendMessage(msg)
        pass

    def sendMessage(self, msg: myMessage.myMessage ):
        self.client_socket.sendall(str(msg).encode(encoding='utf_8', errors='strict'))
        print("i send %s" % msg.action)

    def exitServer(self):
        self.sendMessageAction(myMessage.ActionType.exit)

    def handleResponse(self, response: str):
        msg = myMessage.myMessage(response)
        print("handleResponse")
        if msg.action == myMessage.ActionType.changeBackground:
            self.changeBackground(msg)

    def connectServer(self, Server_HOST, Server_PORT):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((Server_HOST, Server_PORT))


read_ = False


def waitReadAction(client: Client):
    global read_
    while True:
        response = myMessage.readResponse(client.client_socket, log=True)
        print("i read " + response)
        client.handleResponse(response)
        read_ = True




# Server_HOST = '192.168.1.224'
Server_HOST = '192.168.21.1'
Server_PORT = 12345

client = Client()
client.connectServer(Server_HOST, Server_PORT)
client.sendMessageAction(myMessage.ActionType.hello)
print(client.client_socket.getsockname())
print('hello')
thread = threading.Thread(target=waitReadAction,args=(client,))   # 設定線程
thread.start()

while True:
    time.sleep(3)
    client.sendMessageAction(myMessage.ActionType.online)

    print("send online...")

######################################33333

# thread = threading.Thread(target=client.sendMessageAction,args=(myMessage.ActionType.online,))   # 設定線程
# thread.start()

# while True:
#     waitReadAction(client)
#     print("send online...")
#     if read_: break

client.exitServer()