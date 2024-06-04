from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:clearpointdivine@localhost/npl'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here' 
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class UploadedFiles(db.Model):
    file_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    conversion_status = db.Column(db.Boolean, default=False)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    current_user = User.query.filter_by(username=username).first()
    if current_user and check_password_hash(current_user.password_hash, password):
        session['username'] = current_user.username
        session.permanent = True
        return jsonify({'message': 'Login successful', 'username': current_user.username}), 200

    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/form', methods=['POST'])
def form():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    print(data)
    if data:
        return jsonify({'message': 'Form filled successfully'}), 200
    return jsonify({'message': 'Invalid data'}), 400

if __name__ == '__main__':
    app.run(debug=True)