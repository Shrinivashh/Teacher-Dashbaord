from flask import Blueprint, render_template, request, redirect, url_for, session,flash
from .mode import *
from .auth import db_session
from sqlalchemy import func, and_

admin = Blueprint('admin', __name__)


@admin.route('/')
def home():
    return render_template('admin/index.html')

@admin.route('/admin_login', methods=['POST', 'GET'])
def admin_login():
    admin_user = db_session.query(Admin).filter_by(username='admin').first()

    # If the admin user doesn't exist, create one
    if not admin_user:
        admin_user = Admin(username='admin', password='admin')  # Set password directly
        db_session.add(admin_user)
        db_session.commit()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check username and password
        if admin_user.username == username and admin_user.password == password:
            session['admin_logged_in'] = True  # Set session to indicate login
            return redirect(url_for('admin.dashboard'))  # Redirect to dashboard

    return render_template('admin/index.html')

@admin.route('/dashboard')
def dashboard():
    events_today_and_upcoming = db_session.query(Events).filter(Events.date >= datetime.now())
    exams_today_and_upcoming = db_session.query(Exams).filter(Exams.date >= datetime.now())
    student_count = len(db_session.query(Students).all())
    teachers_count = len(db_session.query(Teacher).all())
    class_count = len(db_session.query(Class).all())
    
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin.admin_login'))  
    
    return render_template('admin/dashboard.html',
                           student_count = student_count,
                           teachers_count = teachers_count,
                           class_count = class_count,
                           events_today_and_upcoming = events_today_and_upcoming,
                           exams_today_and_upcoming = exams_today_and_upcoming)


@admin.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        class_id = request.form['class_id']
        phone = request.form['phone']
        address = request.form['address']
        
        # Create the new student record
        new_student = Students(first_name=first_name, last_name=last_name, email=email, class_id=class_id)
        
        # Add the student to the database
        db_session.add(new_student)
        db_session.commit()

        
        
        
        return redirect(url_for('admin.dashboard'))  # Redirect to dashboard after adding the student
    
    # Query available classes to display in the dropdown
    classes = db_session.query(Class).all()
    return render_template('admin/add_student.html', classes=classes)


@admin.route('/add_class', methods=['GET', 'POST'])
def add_class():
    if request.method == 'POST':
        name = request.form['name']
        teacher_id = request.form['teacher_id']
        
   
        new_class = Class(name=name, teacher_id=teacher_id)
        
        db_session.add(new_class)
        db_session.commit()

        return redirect(url_for('admin.dashboard'))  
    

    teachers = db_session.query(Teacher).all()
    return render_template('admin/add_class.html', teachers=teachers)
@admin.route('/delete/<int:class_id>', methods=['GET', 'POST'])
def delete(class_id):
    class_to_delete = db_session.query(Class).filter_by(id=class_id).first()
    
    if class_to_delete:
        db_session.delete(class_to_delete)
        db_session.commit()
        return redirect(url_for('views.classes'))
    else:
        return render_template('error.html', message='Class not found')

@admin.route('/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        username=request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        date_of_birth = request.form['date_of_birth']
        password = request.form['password']
        
        new_teacher = Teacher(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=date_of_birth,
            password=password 
        )
        
        db_session.add(new_teacher)
        db_session.commit()
       
        
        

        return redirect(url_for('admin.dashboard'))  
    
    return render_template('admin/add_teacher.html')


@admin.route('/exams', methods=['POST', 'GET'])
def exams():
    current_time = datetime.now()
    upcoming_exams = db_session.query(Exams).filter(Exams.date > current_time).all()
    past_exams = db_session.query(Exams).filter(Exams.date < datetime.now().time()).all()
    ongoing_exams = db_session.query(Exams).filter(
        and_(
            func.str_to_date(func.substring_index(Exams.time, ' - ', 1), '%I:%i %p') <= current_time.time(),
            func.str_to_date(func.substring_index(Exams.time, ' - ', -1), '%I:%i %p') >= current_time.time()
        )
    ).all()
    return render_template('admin/exam.html', 
                           past_exams=past_exams, 
                           upcoming_exams=upcoming_exams, 
                           ongoing_exams=ongoing_exams)

@admin.route('/add_exams',methods=['POST','GET'])
def add_exams():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        time = request.form['time']
        
        new_exam = Exams(
            name=name,
            date=date,
            time=time
        )
        db_session.add(new_exam)
        db_session.commit()
        return redirect(url_for('admin.exams'))
    return render_template('admin/dashboard.html')

@admin.route('/events',methods=['POST','GET'])
def events():
    past_events = db_session.query(Events).filter(Events.date < datetime.now()).all()
    upcoming_events = db_session.query(Events).filter(Events.date > datetime.now()).all()
    
    
    return render_template('admin/events.html',past_events=past_events,upcoming_events=upcoming_events)

@admin.route('/add_event',methods=['POST','GET'])
def add_event():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        time = request.form['time']
        location = request.form['location']
        description = request.form['description']
        
        new_event = Events(
            name=name,
            date=date,
            time=time,
            location=location,
            description=description
        )
        db_session.add(new_event)
        db_session.commit()
        return redirect(url_for('admin.events'))
    return render_template('admin/events.html')
        
@admin.route('/notifications')
def notifications():
    teachers = db_session.query(Teacher).all()
    teacher_id = 0
    for teacher in teachers:
        teacher_id = teacher.id
    return render_template('admin/notifications.html',
                           teachers=teachers,
                           teacher_id=teacher_id) 
    
    
@admin.route('/assign_teacher', methods=['GET', 'POST'])
def assign_teacher():
    if request.method == 'POST':
        class_id = request.form['class_id']
        teacher_id = request.form['teacher_id']
        
        class_to_update = db_session.query(Class).filter_by(id=class_id).first()
        teacher = db_session.query(Teacher).filter_by(id=teacher_id).first()
        
        class_to_update.teacher_id = teacher.id
        db_session.commit()

        flash('Teacher assigned successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    
    classes = db_session.query(Class).all()
    teachers = db_session.query(Teacher).all()
    
    return render_template('admin/assign_teacher.html', classes=classes, teachers=teachers)


@admin.route('/subjects')
def subjects():
    teachers = db_session.query(Teacher).all()
    classes = db_session.query(Class).all()
    return render_template('admin/subjects.html',teachers=teachers,classes=classes)


@admin.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        description = request.form['description']
        teacher_id = request.form['teacher_id']
        class_id = request.form['class_id']
        
        new_subject = Subjects(
            name=name,
            code=code,
            description=description,
            teacher_id=teacher_id,
            class_id=class_id
        )
        
        db_session.add(new_subject)
        db_session.commit()
        
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/subjects.html')


@admin.route('/assign_subject',methods=['POST','GET'])
def assign_subject():
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        subject_id = request.form['subject_id']
        
        subject_to_update = db_session.query(Subjects).filter_by(id=subject_id).first()
        teacher = db_session.query(Teacher).filter_by(id=teacher_id).first()
        
        subject_to_update.teacher_id = teacher.id
        
        return redirect(url_for('admin.dashboard'))
    teachers = db_session.query(Teacher).all()
    subjects = db_session.query(Subjects).all()
    return render_template('admin/assign_subject.html',teachers=teachers,subjects=subjects)
        
        
        
        
        
        

        



