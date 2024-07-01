from pymongo import MongoClient
import os
import pandas as pd
from prophet import Prophet
import logging



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

file_path = find_file('updated_merged_dataset2_with_calls.csv')

if file_path:
    df = pd.read_csv(file_path)
else:
    raise FileNotFoundError('updated_merged_dataset2_with_calls.csv not found')



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



def user_usage(user_id):
    file_path = find_file('updated_merged_dataset2_with_calls.csv')
    if file_path:
        df = pd.read_csv(file_path)
    else:
        raise FileNotFoundError('updated_merged_dataset2_with_calls.csv not found')
    
    try:
        user_data = df[df['user_id'] == int(user_id)].to_dict(orient='records')
    except Exception as e:
        logging.error(e)
    
    return user_data


def get_predictions(user_id, days_ahead):
    # Use Prophet to predict the next days of data of all 3: internet, messages, and calls
    file_path = find_file('updated_merged_dataset2_with_calls.csv')
    if file_path:
        df = pd.read_csv(file_path)
    else:
        raise FileNotFoundError('updated_merged_dataset2_with_calls.csv not found')
    
    # Get internet usage predictions from the last day of the dataset
    df_internet = df.drop(columns=['plan', 'total_messages_used', 'total_minutes'])
    filtered_internet = df_internet[df_internet['user_id'] == user_id]
    prepped_internet = filtered_internet.drop(columns='user_id')
    prepped_internet = prepped_internet.rename(columns={'session_date': 'ds', 'mb_used': 'y'})
    last_date_internet = prepped_internet['ds'].max()
    model_internet = Prophet()
    model_internet.fit(prepped_internet)
    future_internet = model_internet.make_future_dataframe(periods=days_ahead)
    forecast_internet = model_internet.predict(future_internet)
    # Filter the forecast to start from the last date
    forecast_internet_from_last_date = forecast_internet[forecast_internet['ds'] >= last_date_internet]
    # Extract the required columns
    full_data_internet = forecast_internet_from_last_date[['ds', 'yhat']]
    # Get the last n days of the forecast
    internet_prediction = full_data_internet.head(days_ahead).to_dict(orient='records')
    
    # Get messages usage predictions from the last day of the dataset
    df_messages = df.drop(columns=['plan', 'mb_used', 'total_minutes'])
    filtered_messages = df_messages[df_messages['user_id'] == user_id]
    prepped_messages = filtered_messages.drop(columns='user_id')
    prepped_messages = prepped_messages.rename(columns={'session_date': 'ds', 'total_messages_used': 'y'})
    last_date_messages = prepped_messages['ds'].max()
    model_messages = Prophet()
    model_messages.fit(prepped_messages)
    future_messages = model_messages.make_future_dataframe(periods=days_ahead)
    forecast_messages = model_messages.predict(future_messages)
    # Filter the forecast to start from the last date
    forecast_messages_from_last_date = forecast_messages[forecast_messages['ds'] >= last_date_messages]
    # Extract the required columns
    full_data_messages = forecast_messages_from_last_date[['ds', 'yhat']]
    # Get the last n days of the forecast
    messages_prediction = full_data_messages.head(days_ahead).to_dict(orient='records')
    
    # Get calls usage predictions from the last day of the dataset
    df_calls = df.drop(columns=['plan', 'mb_used', 'total_messages_used'])
    filtered_calls = df_calls[df_calls['user_id'] == user_id]
    prepped_calls = filtered_calls.drop(columns='user_id')
    prepped_calls = prepped_calls.rename(columns={'session_date': 'ds', 'total_minutes': 'y'})
    last_date_calls = prepped_calls['ds'].max()
    model_calls = Prophet()
    model_calls.fit(prepped_calls)
    future_calls = model_calls.make_future_dataframe(periods=days_ahead)
    forecast_calls = model_calls.predict(future_calls)
    # Filter the forecast to start from the last date
    forecast_calls_from_last_date = forecast_calls[forecast_calls['ds'] >= last_date_calls]
    # Extract the required columns
    full_data_calls = forecast_calls_from_last_date[['ds', 'yhat']]
    # Get the last n days of the forecast
    calls_prediction = full_data_calls.head(days_ahead).to_dict(orient='records')
    
    return internet_prediction, messages_prediction, calls_prediction


def get_anomalies(plan):
    if plan == 'surf':
        file_path = find_file('surf_plans_anomalies.csv')
        if file_path:
            plan_data = pd.read_csv(file_path)
            plan_data.drop(columns=['Anomaly'], inplace=True)
            # add "suggested action" column with the following logic:
            # entries in this column depend on the total_mb_used column if the value in total_mb_used is greater than 1 million the 'Suggested Action' value shall be 'Upgrade to Ultimate Plan'
            # if the value in total_mb_used is less than 1 million the 'Suggested Action' value shall be 'No Action Required'
            plan_data['Suggested Action'] = plan_data['total_mb_used'].apply(lambda x: 'Upgrade to Ultimate Plan' if x > 1000000 else 'No Action Required')

            anomalies = plan_data.to_dict(orient='records')
        else:
            raise FileNotFoundError('surf_plans_anomalies.csv not found')
    else:
        file_path = find_file('ultimate_plans_anomalies.csv')
        if file_path:
            plan_data = pd.read_csv(file_path)
            plan_data.drop(columns=['Anomaly'], inplace=True)
            # add "suggested action" column with the following logic:
            # entries in this column depend on the total_mb_used column if the value in total_mb_used is less than 1 million the 'Suggested Action' value shall be 'Downgrade to Surf Plan'
            # if the value in total_mb_used is greater than 10 million the 'Suggested Action' value shall be 'High Usage Detected'
            # if the value in total_mb_used is between 1 million and 10 million the 'Suggested Action' value shall be 'No Action Required'
            plan_data['Suggested Action'] = plan_data['total_mb_used'].apply(lambda x: 'Downgrade to Surf Plan' if x < 1000000 else ('Investigate Usage' if x > 10000000 else 'No Action Required'))
            anomalies = plan_data.to_dict(orient='records')
        else:
            raise FileNotFoundError('ultimate_plans_anomalies.csv not found')
        
    return anomalies