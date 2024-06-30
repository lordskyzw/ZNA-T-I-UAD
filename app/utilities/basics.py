from pymongo import MongoClient
import os
import pandas as pd



mongo_uri = os.getenv('MONGO_URI')

def find_file(filename, search_path="."):
    """
    Searches for a file in the specified directory and its subdirectories.
    :param filename: The name of the file to search for.
    :param search_path: The directory to start searching from.
    :return: The path to the file if found, otherwise None.
    """
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

file_path = find_file('merged_dataset2.csv')

if file_path:
    df = pd.read_csv(file_path)
else:
    raise FileNotFoundError('merged_dataset2.csv not found')



def check_credentials(username, password):
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
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

# def user_usage(user_id):
#     file_path = find_file('merged_dataset2.csv')
#     if file_path:
#         df = pd.read_csv(file_path)
#         print('file found')
#     else:
#         raise FileNotFoundError('merged_dataset2.csv not found')
#     try:
#         user_data = df[df['user_id'] == int(user_id)].to_dict(orient='records')
#         print(user_data)
#     except Exception as e:
#         print(str(e))
#     return user_data

def user_usage(user_id):
    file_path = find_file('merged_dataset2.csv')
    if file_path:
        df = pd.read_csv(file_path)
        print('file found')
        print(df.head())  # Print first few rows to verify structure
    else:
        raise FileNotFoundError('merged_dataset2.csv not found')
    
    try:
        user_data = df[df['user_id'] == int(user_id)].to_dict(orient='records')
        print(user_data)
    except Exception as e:
        print(str(e))
    
    return user_data
