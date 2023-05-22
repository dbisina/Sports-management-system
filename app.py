import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from werkzeug.utils import secure_filename
import threading
import os
import mysql.connector
from flask_mysqldb import MySQL
import random
    
app = Flask(__name__, template_folder='templates')
app.secret_key = "secret_key"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'lcu_database'


mysql = MySQL(app)

def query_db(matric_no):
    cursor = mysql.connection.cursor()
    query = "SELECT passkey FROM Students WHERE matric_no= %s"
    cursor.execute(query, (matric_no,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result[0]
    else:
        return None

def query_db_otp(otp):
    cursor = mysql.connection.cursor()
    query = "SELECT passkey FROM otp WHERE passkey = %s"  # Specify the column name in the WHERE clause
    cursor.execute(query, (otp,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result[0]
    else:
        return None

def save_user(first_name, last_name, matric_no, passkey, department, phone_number):
    cursor = mysql.connection.cursor()
    query = "INSERT INTO Students (first_name, last_name, matric_no, passkey, department, phone_number) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (first_name, last_name, matric_no, passkey, department, phone_number))
    mysql.connection.commit()
    user_id = cursor.lastrowid
    cursor.close()
    return user_id

# Set up file upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'

# Set up allowed file types
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

# Check if a file is an allowed file type
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Homepage
@app.route('/admin_index')
@login_required
def admin_index():
    return render_template('admin_index.html')

@app.route('/user_index')
@login_required
def user_index():
    return render_template('user_index.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle username and password submission
        matric_no = request.form['username']
        passkey = request.form['password']
        stored_password = query_db(matric_no)
        # Process username and password here
        if matric_no == 'admin' and passkey == 'admin':
            session['username'] = matric_no
            return redirect(url_for('admin_index'))
        elif stored_password is not None and stored_password == passkey:
            session['username'] = matric_no
            return redirect(url_for('user_index'))
        else:
            flash('Invalid username or password')

    # Display login form
    return render_template('login.html')


# Logout
@app.route('/logout')
@login_required
def logout():
    session.pop('matric_no', None)
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        matric_no = request.form["matric-no"]
        passkey = request.form["password"]
        confirm_password = request.form["confirm-password"]
        department = request.form["department"]
        phone_number = request.form["phone-number"]

        if passkey != confirm_password:
            flash("Passwords do not match.")
        else:
            user_id = save_user(first_name, last_name, matric_no, passkey, department, phone_number)
            session['matric_no'] = matric_no
            return redirect(url_for('login'))
    return render_template('registeration_user.html')

# Upload file
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File uploaded successfully')
            return redirect(url_for('index'))
        else:
            flash('Invalid file type')
    return render_template('upload.html')

# Download file
@app.route('/download/<filename>')
@login_required
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Edit file
@app.route('/edit/<filename>', methods=['GET', 'POST'])
@login_required
def edit(filename):
    if request.method == 'POST':
        new_text = request.form['text']
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'w') as f:
            f.write(new_text)
            flash('File edited successfully')
            return redirect(url_for('index'))
    else:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as f:
            text = f.read()
        return render_template('edit.html', filename=filename, text=text)



# Delete file
@app.route('/delete/<filename>')
@login_required
def delete(filename):
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    flash('File deleted successfully')




# User management
@app.route("/user_management")
def user_management():
    # Fetch all user data from the database
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM Students"
    cursor .execute(query)
    users = cursor.fetchall()
    cursor.close()
    return render_template('user_management.html', Users=users)

# Add user
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        session['matric_number'] = request.form['matric-number']
        return redirect(url_for('generate_otp'))
    else:
        return render_template('add_user.html')


    
# Route for the Edit User page
@app.route('/edit_user', methods=['GET', 'POST'])
@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    if request.method == 'POST':
        user_id = request.form['user_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        department = request.form['department']
        phone_number = request.form['phone_number']
        
        # Update the user's details in the database
        cursor = mysql.connection.cursor()
        query = "UPDATE Students SET first_name = %s, last_name = %s, department = %s, phone_number = %s WHERE id = %s"
        cursor.execute(query, (first_name, last_name, department, phone_number, user_id))
        mysql.connection.commit()
        cursor.close()
        
        flash('User details updated successfully')
        return redirect(url_for('edit_user'))
    else:
        # Retrieve all users from the database
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM Students"
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        
        return render_template('edit_user.html', users=users)


# Route for the Delete User page
@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        if 'delete_selected' in request.form:
            selected_users = request.form.getlist('selected_users')
            
            # Delete the selected users from the database
            cursor = mysql.connection.cursor()
            for user_id in selected_users:
                query = "DELETE FROM Students WHERE id = %s"
                cursor.execute(query, (user_id,))
            mysql.connection.commit()
            cursor.close()
            
            flash('Selected users deleted successfully')
        elif 'delete_all' in request.form:
            # Delete all users from the database
            cursor = mysql.connection.cursor()
            query = "DELETE FROM Students"
            cursor.execute(query)
            mysql.connection.commit()
            cursor.close()
            
            flash('All users deleted successfully')
        
        return redirect(url_for('delete_user'))
    else:
        # Retrieve all users from the database
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM Students"
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        
        return render_template('delete_user.html', users=users)



# Disable user
@app.route('/disable-user/<user_id>')
@login_required
def disable_user(user_id):
    # code to disable the specified user goes here
    flash('User disabled successfully')
    return redirect(url_for('user_management'))


# System configuration
@app.route('/system-configuration', methods=['GET', 'POST'])
@login_required
def system_configuration():
    if request.method == 'POST':
        # code to update the system configuration goes here
        flash('System configuration updated successfully')
        return redirect(url_for('system_configuration'))
    else:
        # code to retrieve the current system configuration goes here
        return render_template('system-configuration.html')

# Back up system
@app.route('/backup-system')
@login_required
def backup_system():
    # code to back up the system goes here
    flash('System backed up successfully')
    return redirect(url_for('index'))

# Manage logs
@app.route('/manage-logs')
@login_required
def manage_logs():
    # code to retrieve and display the system logs goes here
    return render_template('manage-logs.html')


    
if __name__ == '__main__':
    app.run(debug=True)




print('             ~lyon98.dbios')

from flask_stripe import Stripe

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['STRIPE_PUBLIC_KEY'] = 'your_stripe_public_key'
app.config['STRIPE_SECRET_KEY'] = 'your_stripe_secret_key'
stripe = Stripe(app)

# Payment processing page
@app.route('/payment', methods=['POST'])
def payment():
    # Retrieve payment information from the form
    amount = request.form['amount']
    currency = 'usd'
    payment_method = request.form['payment_method']
    
    # Process the payment
    try:
        stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            confirm=True
        )
        # Payment successful, update finances accordingly
        # Add your code to update the finances database or perform other actions
        
        return 'Payment successful!'
    except Exception as e:
        return 'Payment failed. Error: ' + str(e)


# Finances page
@app.route('/finances')
def finances():
    return render_template('finances.html')

# Financial reports page
@app.route('/financial-reports')
def financial_reports():
    return render_template('financial_reports.html')


# Reports and analytics page
@app.route('/reports')
def reports():
    return render_template('reports.html')

# Dashboard page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# API endpoint to retrieve student information
@app.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    # Logic to retrieve student information from the student information system
    student_info = {
        'id': student_id,
        'name': 'John Doe',
        'major': 'Computer Science',
        'year': 'Junior'
    }
    return jsonify(student_info)


# API endpoint to process payment
@app.route('/api/payment', methods=['POST'])
def process_payment():
    payment_data = request.json
    # Logic to process payment using a payment gateway or library
    # You can integrate with a third-party payment gateway or implement your own payment processing logic here
    # Return the payment response as JSON
    payment_response = {
        'status': 'success',
        'message': 'Payment processed successfully'
    }
    return jsonify(payment_response)