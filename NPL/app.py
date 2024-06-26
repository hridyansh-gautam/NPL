from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta
import os
import registration
import pandas as pd
import checksum

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:clearpointdivine@localhost/npl'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/custlogin', methods=['GET', 'POST'])
def custlogin():
    if request.method == 'GET':
        return render_template('custlogin.html')
    elif request.method == 'POST':
        data = request.get_json()
        email = data.get('username')
        password = data.get('password')
        captchaToken = data.get('captchaToken')

        if not email or not password or not captchaToken:
            return jsonify({'message': 'Email, password, and CAPTCHA are required'}), 400

        if registration.check_org_credentials(email, password):
            session['username'] = email
            session.permanent = True
            return jsonify({'message': 'Login successful', 'username': email}), 200

        return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/emplogin', methods=['GET', 'POST'])
def emplogin():
    if request.method == 'GET':
        return render_template('emplogin.html')
    elif request.method == 'POST':
        data = request.get_json()
        email = data.get('username')
        password = data.get('password')
        captchaToken = data.get('captchaToken')

        if not email or not password or not captchaToken:
            return jsonify({'message': 'Email, password, and CAPTCHA are required'}), 400

        user_info = registration.check_emp_credentials(email, password)
        if user_info:
            session['username'] = email
            session.permanent = True
            return jsonify({
                'message': 'Login successful',
                'username': email,
                'designation': user_info['designation']
            }), 200

        return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    
    return redirect( url_for('home') )

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/indregister', methods=['GET', 'POST'])
def indregister():
    if request.method == 'GET':
        return render_template('indregister.html')
    elif request.method == 'POST':
        data = request.form
        data_dict = {
            'f_name': data.get('firstName'),
            'l_name': data.get('lastName'),
            'mobile_no': data.get('phone'),
            'email': data.get('email'),
            'alt_email': data.get('altEmail'),
            'addr_1': data.get('addressLine1'),
            'addr_2': data.get('addressLine2'),
            'country': data.get('country'),
            'state': data.get('state'),
            'city': data.get('city'),
            'pincode': data.get('pincode'),
            'password': data.get('newPassword')
        }
        if data_dict['password'] != data.get('confirmPassword'):
            return jsonify({'message': 'Passwords do not match'}), 400
        response = registration.add_new_ind(data_dict)
        print(response)
        return jsonify({'message': 'Registration successful', 'username': data_dict['f_name'] + ' ' + data_dict['l_name']}), 200

@app.route('/orgregister', methods=['GET', 'POST'])
def orgregister():
    if request.method == 'GET':
        return render_template('orgregister.html')
    elif request.method == 'POST':
        data = request.form
        data_dict = {
            'org_type': data.get('orgType'),
            'org_name': data.get('orgName'),
            'gst_no': data.get('gst'),
            'phone': data.get('phone'),
            'landline': data.get('landline'),
            'email': data.get('email'),
            'alt_email': data.get('altEmail'),
            'addr_1': data.get('addressLine1'),
            'city': data.get('city'),
            'state': data.get('state'),
            'country': data.get('country'),
            'pincode': data.get('pincode'),
            'password': data.get('newPassword'),
        }
        if data_dict['password'] != data.get('confirmPassword'):
            return jsonify({'message': 'Passwords do not match'}), 400

        response = registration.add_new_org(data_dict)
        print(response)
        return jsonify({'message': 'Registration successful', 'username': data_dict['org_name']}), 200

@app.route('/empregister', methods=['GET', 'POST'])
def empregister():
    if request.method == 'GET':
        return render_template('empregister.html')
    elif request.method == 'POST':
        data = request.form
        data_dict = {
            'f_name': data.get('firstName'),
            'l_name': data.get('lastName'),
            'emp_id': data.get('employeeId'),
            'mobile_no': data.get('phone'),
            'designation': data.get('designation'),
            'email': data.get('email'),
            'addr_1': data.get('addressLine1'),
            'password': data.get('newPassword'),
        }
        if data_dict['password'] != data.get('confirmPassword'):
            return jsonify({'message': 'Passwords do not match'}), 400
        
        response = registration.add_new_emp(data_dict)
        print(response)
        return jsonify({'message': 'Registration successful', 'username': data_dict['f_name'] + ' ' + data_dict['l_name']}), 200

@app.route('/admwelcome')
def admwelcome():
    return render_template('admwelcome.html')

@app.route('/empwelcome')
def empwelcome():
    return render_template('empwelcome.html')

@app.route('/custwelcome')
def custwelcome():
    return render_template('custwelcome.html')

@app.route('/ctbr')
def ctbr():
    return render_template('ctbr.html')

@app.route('/dcc')
def dcc():
    return render_template('dcc.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/add_new_service')
def add_new_service():
    data_folder = 'data'
    excel_files = [file for file in os.listdir(data_folder) if file.endswith('.xlsx')]
    dataframes = []
    filenames = []

    for file in excel_files:
        file_path = os.path.join(data_folder, file)
        df = pd.read_excel(file_path)
        filenames.append(file)
        dataframes.append(df.to_html(classes="table table-striped", index=False))

    return render_template('display_sheets.html', dataframes=dataframes, filenames=filenames, enumerate=enumerate)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)