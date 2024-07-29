from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct, create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta
import os
import registration 
import meteorological
import pandas as pd
import checksum
from dotenv import load_dotenv
from generate_pdf import Generator


app = Flask(__name__)
CORS(app, supports_credentials=True)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = 'uploads'
UPLOAD_FOLDER = 'uploads'

db = SQLAlchemy(app)
pdf_generator = Generator()

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

        customer = registration.check_cust_credentials(email, password)
        if customer:
            session['username'] = email
            session['cust_reg_id'] = customer['cust_reg_id']
            session.permanent = True
            return jsonify({'message': 'Login successful', 'username': email, 'id': customer['cust_reg_id']}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

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
            session['emp_reg_id'] = user_info['emp_reg_id']
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
    session.pop('cust_reg_id', None)
    
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
        file = request.files['signature']
        if file:
            signature_binary = file.read()
        else:
            return jsonify({'message': 'Signature is required'}), 400
        data_dict = {
            'f_name': data.get('firstName'),
            'l_name': data.get('lastName'),
            'emp_id': data.get('employeeId'),
            'mobile_no': data.get('phone'),
            'designation': data.get('designation'),
            'email': data.get('email'),
            'addr_1': data.get('addressLine1'),
            'password': data.get('newPassword'),
            'signature': signature_binary
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
        data = request.form.to_dict()
        ind_id = data.get('ind_reg')
        org_id = data.get('org_reg')
        if ind_id:
            user_data = registration.get_one_ind(ind_id)
            cust_data = {
                'cust_type': 'Individual',
                'cust_name': user_data['f_name'] + ' ' + user_data['l_name'],
                'cust_email': user_data['email'],
                'alt_email': user_data['alt_email'],
                'mobile_no': user_data['mobile_no'],
                'cust_addr_1': user_data['addr_1'],
                'cust_addr_2': user_data['addr_2'],
                'country': user_data['country'],
                'state': user_data['state'],
                'city': user_data['city'],
                'pincode': user_data['pincode'],
                'password': user_data['password']
            }
            print(registration.add_new_cust(cust_data))
            print(registration.delete_org(ind_id))
        else:
            user_data = registration.get_one_ind(org_id)
            cust_data = {
                'cust_type': user_data['org_type'],
                'cust_name': user_data['org_name'],
                'cust_email': user_data['email'],
                'alt_email': user_data['alt_email'],
                'gst_no': user_data['gst_no'],                
                'mobile_no': user_data['phone'],
                'landline_no': user_data['landline'],
                'cust_addr_1': user_data['addr_1'],
                'country': user_data['country'],
                'state': user_data['state'],
                'city': user_data['city'],
                'pincode': user_data['pincode'],
                'password': user_data['password']
            }
            print(registration.add_new_cust(cust_data))
            print(registration.delete_org(org_id))
        ind_list = registration.get_ind()
        org_list = registration.get_org()
        return render_template('add_cust.html', ind_list=ind_list, org_list=org_list)

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

services_data = {
        'service_code': '',
        'parameter': '',
        'item_type_group': '',
        'item_name': '',
        'alias_name': '',
        'range': '',
        'calibration_parameters': '',
        'no_of_points_for_calibration_procedure_no': '',
        'limitation_condition': '',
}

charges_data = {
    'service_code': '',
    'charges_per_item_rs': '',
    'additional_charges_rs': '',
    'description_for_additional_charges': '',
    'remarks_if_any': ''
}

@app.route('/ctbr1', methods=['GET', 'POST'])
def ctbr1():
    if request.method == 'GET':
        cust_reg_id = session.get('cust_reg_id')
        if cust_reg_id:
            customer = registration.get_cust(int(cust_reg_id))
            classifications = meteorological.get_classification()
            return render_template('ctbr1.html', customer=customer, classifications=classifications)
        else:
            return render_template('ctbr1.html', customer=None)

@app.route('/ctbr2', methods=['GET', 'POST'])
def ctbr2():
    if request.method == 'GET':
        cust_reg_id = session.get('cust_reg_id')
        if cust_reg_id:
            customer = registration.get_cust(int(cust_reg_id))
            classifications = meteorological.get_classification()
            return render_template('ctbr2.html', customer=customer, classifications=classifications)
        else:
            return render_template('ctbr2.html', customer=None)
    elif request.method == 'POST':
        if request.form:
            key = next(iter(request.form))
            value = request.form.get(key)

            column_map = {
                'categorySelect': 'service_code',
                'parametersSelect': 'parameter',
                'itemTypeSelect': 'item_type_group',
                'itemNameSelect': 'item_name',
                'aliasNameSelect': 'alias_name',
                'rangeSelect': 'range',
                'calibrationParametersSelect': 'calibration_parameters',
                'pointsSelect': 'no_of_points_for_calibration_procedure_no',
                'limitationSelect': 'limitation_condition',
                'chargesSelect': 'charges_per_item_rs',
                'additionalChargesSelect': 'additional_charges_rs',
                'descriptionSelect': 'description_for_additional_charges',
                'remarksSelect': 'remarks_if_any'
            }

            column = column_map.get(key)

            if column:
                if column in services_data:
                    if services_data[column]:
                        for key in services_data:
                            services_data[key] = ''
                    services_data[column] = value
                services = meteorological.get_services(services_data)
                if column in charges_data:
                    if charges_data[column]:
                        for key in charges_data:
                            charges_data[key] = ''
                    charges_data[column] = value
                charges = meteorological.get_service_charges(charges_data)
                return jsonify({'services': services, 'charges': charges})
        
        return jsonify({'error': 'Invalid request'}), 400

@app.route('/send_charges', methods=['POST'])
def send_charges():
    data = request.get_json()
    totalCharge = data.get('totalCharge')
    print(f"Stored totalCharge: {totalCharge}")
    session['totalCharge'] = totalCharge    
    return jsonify({"status": "success", "totalCharge": totalCharge})

@app.route('/ctbr3', methods=['GET'])
def ctbr3():
    totalCharge = session.get('totalCharge')
    print(f"Received totalCharge: {totalCharge}")
    return render_template('ctbr3.html', totalCharge=totalCharge)

@app.route('/ctbr4', methods=['GET', 'POST'])
def ctbr4():
    if request.method == 'GET':
        return render_template('ctbr4.html')
    elif request.method == 'POST':
        return jsonify({'error': 'Invalid request'}), 400

@app.route('/ctbr5', methods=['GET', 'POST'])
def ctbr5():
    if request.method == 'GET':
        return render_template('ctbr5.html')
    elif request.method == 'POST':
        return jsonify({'error': 'Invalid request'}), 400

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

@app.route('/dcc2')
def dcc2():
    return render_template('dcc2.html')

@app.route('/download-template/<certificate_type>')
def download_template(certificate_type):
    template_file = f"{certificate_type}_template.xlsx"
    template_path = os.path.join('static/excel_templates', template_file)
    if os.path.exists(template_path):
        return send_from_directory(directory='static/excel_templates', path=template_file, as_attachment=True)
    else:
        return "Template not found", 404

@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    if 'excelFile' not in request.files:
        return jsonify(success=False), 400

    excel_file = request.files['excelFile']
    graph_img = request.files['graphImg']
    if excel_file.filename == '':
        return jsonify(success=False), 400
    
    user_id = str(session['emp_reg_id'])
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 403

    user_folder = os.path.join(UPLOAD_FOLDER, user_id)
    os.makedirs(user_folder, exist_ok=True)

    excel_file.save(os.path.join(user_folder, excel_file.filename))
    if graph_img.filename:
        graph_img.save(os.path.join(user_folder , graph_img.filename))
    data = request.form
    attach_data = True if data.get('embed') == 'True' else False
    attach_graph = True if data.get('graph') == 'True' else False
    doc_type=data.get('certificateType')
    excel_path = f'./uploads/{user_id}/{excel_file.filename}'
    graph_path = f'./uploads/{user_id}/{graph_img.filename}' if attach_graph else ''
    
    pdf_name, pdf_data =  pdf_generator.execute_pdf_generator( excel_path, doc_type)

    if checksum.pdf_exists(pdf_name):
        print('true')
    else:
        pdf_generator.create_pdf(pdf_data, excel_path, pdf_name, doc_type, graph_path, attach_data, attach_graph)
        checksum.insert_pdf_record(
            pdf_directory=f'./static/pdfs/{pdf_name}',
            current_stage=2,
            calibrated_by=pdf_data['calibrated_by'] if pdf_data['calibrated_by'] else pdf_data['tested_by'],
            checked_by=pdf_data['checked_by'],
            scientist_in_charge=pdf_data['incharge'],
            issued_by=pdf_data['issued_by'],
        )
        
    
    return jsonify(success=True)

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