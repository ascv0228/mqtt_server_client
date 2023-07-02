import socket, sys 
import threading 
# from ..client import myMessage
import myMessage
import time

import mdatabases

# 此程式碼修改自
# http://hhtucode.blogspot.com/2013/03/python-simple-socket-server.html


device_sockets = dict()
collection = mdatabases.get_collection()

def threadWork(client_socket: socket):
    hello = False # 先確認是否經過hello
    try:
        while True:
            msg = client_socket.recv(1024).decode(encoding='utf_8', errors='strict')
            msg = myMessage.myMessage(msg)
            print("Client send: %s" % msg )
            if not msg:
                pass
            elif msg.getTargetDevice() != myMessage.DeviceType.server:
                device_id = msg.getSourceDeviceId()
                device = msg.getSourceDevice()

                if device == myMessage.DeviceType.client:
                    mdatabases.getDeviceIdFromClient(collection, device_id)
            else:
                if not hello:
                    if msg.action == myMessage.ActionType.hello:
                        hello = True
                        device_id = msg.getSourceDeviceId()
                        device_sockets[device_id] = client_socket
                        sendMsg = myMessage.myMessage({
                            "targetDeviceId" : device_id,
                            "targetDevice" : myMessage.DeviceType.device,
                            "sourceDeviceId" : '',
                            "sourceDevice" : myMessage.DeviceType.server,
                            "action" : myMessage.ActionType.changeBackground,
                            "parameters" : {
                                'url': 'https://benic360.com/wp-content/uploads/2023/01/%E6%88%91%E5%B0%B1%E7%88%9B.png'
                            }
                        })
                        while True:
                            device_sockets[device_id].sendall(str(sendMsg).encode(encoding='utf_8', errors='strict'))
                            print("Send")
                            time.sleep(3)
                    continue
                if msg.action == myMessage.ActionType.exit:
                    client_socket.close()
                # client_socket.send(text.encode(encoding='utf_8', errors='strict'))
    except: pass



HOST, PORT = '0.0.0.0', 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print('wait client...')
while True:
    client_socket, client_address = server_socket.accept()
    print('client connect', client_address)
    thread = threading.Thread(target=threadWork,args=(client_socket,))   # 設定線程
    thread.start()

server_socket.close()