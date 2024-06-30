from flask import Flask, request, session, render_template, jsonify
from flask_cors import CORS
from utilities.basics import check_credentials, user_usage, get_predictions
from dotenv import load_dotenv
import logging
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
CORS(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logging.info(f'Username: {username}, Password: {password}')

        if check_credentials(username, password):
            session.permanent = True
            session['username'] = username

            return render_template('analysis.html')
        else:
            return 'Login Failed', 401

    return render_template('login.html')

@app.route('/user_usage/<int:user_id>', methods=['GET'])
def check_usage(user_id):
    if 'username' not in session:
        return 'Unauthorized', 401
    
    try:
        print(f'User ID: {user_id}')
        user_data = user_usage(user_id)
        if not user_data:
            return 'User data not found', 404
        return jsonify(user_data), 200
    except Exception as e:
        return str(e), 400


@app.route('/predict/<int:user_id>', methods=['GET'])
def predict(user_id):
    if 'username' not in session:
        return 'Unauthorized', 401
    
    try:
        print(f'PREDICTION User ID: {user_id}')
        internet_prediction, messages_prediction, calls_prediction = get_predictions(user_id=user_id, days_ahead=7)
        
        response = {
            'internet_prediction': internet_prediction,
            'messages_prediction': messages_prediction,
            'calls_prediction': calls_prediction
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return str(e), 400

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return 'Logged Out', 200

if __name__ == '__main__':
    app.run(debug=True)
