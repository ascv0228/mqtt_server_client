from pymongo import MongoClient, collection as Collection
from datetime import datetime

def get_collection():
    uri = f'mongodb+srv://ascv0228:AScv0228@g-bot.28g0j.mongodb.net/G-Bot?retryWrites=true&w=majority'
    mclient = MongoClient(uri)
    return mclient['mqtt']['mqtt_data']

def setBind(collection, device_id, client):
        collection.insert_one({
        "data_type" : "bind",
        "client" : client,
        "device_id" : device_id
    })

def getBindClientFromDeviceId(collection, device_id):
    filterRule = {
        "data_type" : "bind",
        "device_id" : device_id
    }
    return collection.find(filterRule)

def getBindDeviceIdFromClient(collection, client):
    filterRule = {
        "data_type" : "bind",
        "client" : client
    }
    return collection.find(filterRule)

def setDeviceIdOnlineTime(collection: Collection, device_id, last_time):
    filterRule = {
        "data_type" : "online",
        "device_id" : device_id
    }
    item = {
        "data_type" : "online",
        "device_id" : device_id,
        "last_time" : last_time
    }
    return collection.update_one(filter=filterRule, update={"$set": item}, upsert=True)

def getDeviceIdOnlineTime(collection, device_id):
    filterRule = {"data_type": "online", "device_id" : device_id }
    item = collection.find_one(filterRule)
    if item != None:
        return item['last_time']
    print("i am none")
    return None

def getRegister():
    pass

def insertItem(collection, item):
    collection.insert_one(item)
  
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
  
    # Get the database
    collection = get_collection()
    now = datetime.now().time()
    # print(now)
    item = {
        "mqtt_device" : "123",
        "client_device" : "8787",
        # "last_time" : now.timestamp()
    }
    # insertItem(collection, item)posts.insert_one(post).inserted_id


    print(getDeviceIdOnlineTime(collection, "112233"))
    # item_details = collection.find()
    # for item in item_details:
    #     # This does not give a very readable output
    #     print(item)


# {
#     "data_type" : "bind",
#     "client" : ...,
#     "device_id" : ...
# }

# {
#     "data_type" : "register",
#     "..." : 建立ID
# }

# {
#     "data_type" : "online",
#     "device_id" : ...,
#     "last_time" : str(int(time.time))
# }