
import json


class myMessage:
    def __init__(self, *args):
        if len(args) >= 1:
            if isinstance(args[0], str):
                data_dict = json.loads(args[0])[0] # 最外層有括號
            elif isinstance(args[0], dict):
                data_dict = args[0]
            else:
                raise "Message Initialize Error"
            
            self.targetDeviceId = data_dict["targetDeviceId"]
            self.targetDevice = data_dict["targetDevice"]
            self.sourceDeviceId = data_dict["sourceDeviceId"]
            self.sourceDevice = data_dict["sourceDevice"]
            self.action = data_dict["action"]
            self.setParameters(data_dict["parameters"])
        else:
            pass

    def getTargetDeviceId(self):
        return self.targetDeviceId
    
    def setTargetDeviceId(self, targetDeviceId):
        self.targetDeviceId = targetDeviceId
        return self

    def getTargetDevice(self):
        return self.targetDevice
    
    def setTargetDevice(self, targetDevice):
        self.targetDevice = targetDevice
        return self

    def getSourceDeviceId(self):
        return self.sourceDeviceId
    
    def setSourceDeviceId(self, sourceDeviceId):
        self.sourceDeviceId = sourceDeviceId
        return self

    def getSourceDevice(self):
        return self.sourceDevice
    
    def setSourceDevice(self, sourceDevice):
        self.sourceDevice = sourceDevice
        return self

    def getAction(self):
        return self.action
    
    def setAction(self, action):
        self.action = action
        return self

    def getParameters(self):
        return self.parameters
    
    def setParameters(self, parameters):
        if isinstance(parameters, str):
            if parameters == '':
                self.parameters = ""
                return
            self.parameters = json.loads(parameters)
        else:
            self.parameters = parameters

    def __str__(self):
        messageJson = [
            {
                "targetDeviceId" : str(self.targetDeviceId),
                "targetDevice" : str(self.targetDevice),
                "sourceDeviceId" : str(self.sourceDeviceId),
                "sourceDevice" : str(self.sourceDevice),  # source: ['client', 'device', 'server']
                "action" : str(self.action), # action: ['online', 'changeBackground']
                # "parameters" : json.dumps(self.parameters)
                "parameters" : self.parameters
            }
        ]
        return json.dumps(messageJson)

def readResponse(socket, log = False):
    received_data = b''
    while True:
        data = socket.recv(1024)
        if not data:
            break
        received_data += data
        if(log):
            print("received_data", received_data)
        if len(data) < 1024:
            break
    response = received_data.decode(encoding='utf_8', errors='strict')

    if(log):
        print("response", response)
    return response



class ActionType:
    ACK = 'ACK'
    online = 'online'
    checkOnline = 'checkOnline'
    resultOnline = 'resultOnline'
    changeBackground = 'changeBackground'
    hello = 'hello' # 告訴伺服器 自己是什麼裝置
    exit = 'exit'
    bind = 'bind' # 手機端發起 綁定

class DeviceType:
    client = 'client'
    device = 'device'
    server = 'server'
    none = ''


# checkOnline
# {
#   parameters = [device_ids]
# }

# resultOnline
# {
#   result = [
#       {
#            "device_id" : device_id,
#            "last_time" : last_time
#       },
#       .....
#  ]
# 
# 
# }