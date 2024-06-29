from pymongo import MongoClient
import os

def check_credentials(username, password):
    # Connect to MongoDB
    client = MongoClient(os.environ.get("MONGO_URI"))
    db = client['ZNA']
    collection = db['users']  

    # Query the database for the credentials
    user = collection.find_one({'username': username, 'password': password})

    # Close the connection
    client.close()

    # Return True if user exists, else False
    if user:
        return True
    else:
        return False
