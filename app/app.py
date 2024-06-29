from flask import Flask, request, session, render_template
from flask_cors import CORS
from utilities.basics import check_credentials

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']

        if check_credentials(username, password):
            session.permanent = True
            session['username'] = username
            return 'Login Successful', 200
        else:
            return 'Login Failed', 401

    return render_template('login.html')

@app.route('/endpoint2', methods=['POST'])
def endpoint2():
    if 'username' not in session:
        return 'Unauthorized', 401

    # Handle logic for endpoint2
    return 'Endpoint 2'

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return 'Logged Out', 200

if __name__ == '__main__':
    app.run()
