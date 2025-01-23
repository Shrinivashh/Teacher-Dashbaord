from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .mode import *  # Assuming this imports Teacher and other models
from sqlalchemy.orm import sessionmaker

auth = Blueprint('auth', __name__)

Session = sessionmaker(engine)
db_session = Session()

@auth.route('/create_account', methods=['POST', 'GET'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['dob']

        # Check if email already exists
        existing_teacher = db_session.query(Teacher).filter_by(email=email).first()
        if existing_teacher:
            return render_template('create_account.html', error='Email already exists')
        
        # Create new teacher account with plain-text password
        new_teacher = Teacher(
            username=username,
            email=email,
            password=password,  # Store password in plain text
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth
        )
        
        db_session.add(new_teacher)
        db_session.commit()

        # Log the user in immediately after account creation
        session['username'] = username
        session['email'] = email
        session['first_name'] = first_name
        session['last_name'] = last_name
        session['date_of_birth'] = date_of_birth
        
        return redirect(url_for('views.dashboard'))

    return render_template('create_account.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query user by username
        user = db_session.query(Teacher).filter_by(username=username).first()

        # Check if user exists and if password matches (in plain text)
        if user and user.password == password:  # Compare plain-text passwords
            session['username'] = user.username
            session['email'] = user.email
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            session['date_of_birth'] = user.date_of_birth
            session['id'] = user.id
            return redirect(url_for('views.dashboard'))
        else:
            flash('Invalid username or password!', 'error')  # Error message for invalid login

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('views.home'))


@auth.route('/account', methods=['POST', 'GET'])
def account():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    username = session.get('username')
    email = session.get('email')
    first_name = session.get('first_name')
    last_name = session.get('last_name')
    dob = session.get('date_of_birth')
    
    return render_template('account.html', 
                           username=username, 
                           email=email, 
                           first_name=first_name, 
                           last_name=last_name, 
                           dob=dob)


@auth.route('/change_password', methods=['POST', 'GET'])
def change_password():
    if request.method == 'POST':
        current_password = request.form['current-password']
        new_password = request.form['new-password']
        confirm_password = request.form['confirm-password']
        
        teacher = db_session.query(Teacher).filter(Teacher.username == session.get('username')).first()
        
        if teacher.password == current_password:  # Check current password in plain text
            if new_password == confirm_password:
                teacher.password = new_password  # Update to new plain-text password
                db_session.commit()
                return redirect(url_for('auth.account'))
            else:
                return render_template('change_password.html', error='Passwords do not match')

    return render_template('change_password.html')


@auth.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        password = db_session.query(Teacher).filter(Teacher.email == email).all()
    
        return render_template('forgot_password.html',password=password)
