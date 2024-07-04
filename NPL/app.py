from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta
import os
import registration
import meteorological
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

        if registration.check_cust_credentials(email, password):
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
    
    return redirect(url_for('home'))

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

@app.route('/admwelcome/add_cust', methods=['GET', 'POST'])
def add_cust():
    if request.method == 'GET' :
        ind_list = registration.get_ind()
        org_list = registration.get_org()
        return render_template('add_cust.html', ind_list=ind_list, org_list=org_list)
    elif request.method == 'POST': 
        data = request.form
        print(data)
        print(data.get('ind'))
        print(data.get('org'))
        return render_template('add_cust.html')

@app.route('/admwelcome/add_service', methods=['GET', 'POST'])
def add_service():
    if request.method == 'GET':
        return render_template('add_service.html')
    elif request.method == 'POST':
        service_details = {
            'service_code': request.form['service_code'],
            'parameter': request.form['parameter'],
            'item_type_group': request.form['item_type_group'],
            'item_name': request.form['item_name'],
            'alias_name': request.form['alias_name'],
            'range': request.form['range'],
            'calibration_parameters': request.form['calibration_parameters'],
            'no_of_points_for_calibration_procedure_no': request.form['no_of_points_for_calibration_procedure_no'],
            'limitation_condition': request.form['limitation_condition'],
            'sample_requirements': request.form['sample_requirements']
        }
        service_charges = {
            'service_code': request.form['service_code'],
            'charges_per_item_rs': request.form['charges_per_item_rs'],
            'additional_charges_rs': request.form['additional_charges_rs'],
            'description_for_additional_charges': request.form['description_for_additional_charges'],
            'remarks_if_any': request.form['remarks_if_any'],
            'normal': request.form['normal'],
            'tatkal': request.form['tatkal'],
            'edc': request.form['edc']
        }
        try:
            print(service_details)
            print(service_charges)
            meteorological.add_new_service(service_details)
            meteorological.add_new_service_charges(service_charges)
            flash('Service and charges added successfully', 'success')
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')
        return redirect(url_for('add_service'))
            
@app.route('/empwelcome')
def empwelcome():
    return render_template('empwelcome.html')

@app.route('/custwelcome')
def custwelcome():
    service_types = db.session.query(distinct(meteorological.meteorological_classification.c.service_types)).all()
    service_types = [row[0] for row in service_types]
    return render_template('custwelcome.html', service_types=service_types)

@app.route('/ctbr', methods=['GET', 'POST'])
def ctbr():
    if request.method == 'GET':
        return render_template('ctbr.html', customer=None)  
    elif request.method == 'POST':
        cust_reg_id = request.form.get('cust_reg_id')  
        if cust_reg_id:
            customer = registration.get_cust(int(cust_reg_id))
            return render_template('ctbr.html', customer=customer)
        else:
            return render_template('ctbr.html', customer=None)

@app.route('/verify/<checksum>')
def verify(checksum):
    response = registration.get_checksum(checksum=checksum)
    if response and response.status == 'active':
        return jsonify({'message': 'Checksum verification successful', 'checksum': checksum, 'certificate no.': response.certificate_no}), 200
    else:
        return jsonify({'message': 'Checksum verification failed'}), 400

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

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)