from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from werkzeug.utils import secure_filename
import sqlite3
import threading
import os

app = Flask(__name__, template_folder='templates')

app.secret_key = "secret_key"

# Check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Homepage
@app.route('/')
@login_required
def admin_index():
    return render_template('admin_index.html')

@app.route('/')
@login_required
def user_index():
    return render_template('user_index.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle username and password submission
        username = request.form['username']
        password = request.form['password']
        stored_password = query_db(username)
        # Process username and password here
        if username == 'admin' and password == 'admin':
            session['username'] = username
            return redirect(url_for('admin_index')) 
        elif stored_password is not None and stored_password == password:
            session['username'] = username
            return redirect(url_for('user_index'))                
        else:
            flash('Invalid username or password')
    # Display login form
    return render_template('login.html')



if __name__ == '__main__':
    app.run(debug=True)