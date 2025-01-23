from flask import Blueprint, render_template, request, redirect, url_for, session,flash
from .mode import *  
from .auth import db_session
from datetime import datetime
from sqlalchemy import and_, case, desc, func
from collections import defaultdict

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('Home.html')

@views.route('/dashboard')
def dashboard():
    teacher_id = session.get('id')
    classes = db_session.query(Class).filter_by(teacher_id=teacher_id).all()
    students = db_session.query(Students).all()
    session['total_students'] = len(students)
    session['total_classes'] = len(classes)
    
    events_upcoming = db_session.query(Events).filter(Events.date >= datetime.now()).all()
    exams_upcoming = db_session.query(Exams).filter(Exams.date >= datetime.now()).all()
    teacher_notifications = db_session.query(Notifications).filter(Notifications.teacher_id == teacher_id).all()
    return render_template('dashboard.html',
                           events_upcoming=events_upcoming,
                           exams_upcoming=exams_upcoming,
                           teacher_notifications=teacher_notifications)

@views.route('/classes', methods=['GET', 'POST'])
def classes():
    teacher_id = session.get('id')  
    if not teacher_id:
        return redirect(url_for('auth.login'))  
    
    classes = db_session.query(Class).filter_by(teacher_id=teacher_id).all()
    
   

    return render_template('classes.html', classes=classes)

@views.route('/delete/<int:class_id>', methods=['GET', 'POST'])
def delete(class_id):
    class_to_delete = db_session.query(Class).filter_by(id=class_id).first()
    
    if class_to_delete:
        db_session.delete(class_to_delete)
        db_session.commit()
        return redirect(url_for('views.classes'))
    else:
        return render_template('error.html', message='Class not found')

@views.route('/show_class/<int:class_id>', methods=['POST', 'GET'])
def show_class(class_id):
    teacher_id = session.get('id')
    class_details = db_session.query(Class).filter_by(id=class_id).first()
    subjects_and_teachers = db_session.query(Subjects.name, Teacher.first_name) \
    .join(Teacher, Teacher.id == Subjects.teacher_id) \
    .join(Class, Class.id == Subjects.class_id) \
    .filter(Teacher.id == teacher_id) \
    .filter(Class.id == class_id) \
    .all()
    if class_details:
        students = db_session.query(Students).filter_by(class_id=class_id).all()
        return render_template('show_class.html', 
                               class_details=class_details, 
                               students=students,
                               subjects_and_teachers=subjects_and_teachers)
    else:
        return render_template('error.html', message='Class not found')



@views.route('/student/<int:student_id>',methods=['POST','GET'])
def student(student_id):
    student = db_session.query(Students).filter_by(id=student_id).first()
    
    exams = db_session.query(Exams).filter(Exams.date >= datetime.now()).all()
    
    attendance_list = db_session.query(Attendance).filter_by(student_id=student_id).all()
    present_count = 0
    absent_count = 0
    present_percentage = 0
    attendance_days = []
    for date in attendance_list:
        attendance_days.append(date.date)
        
    
    for absent in attendance_list:
        if absent.status == 'absent':
            absent_count += 1
    
    for present in attendance_list:
        if present.status == 'present':
            present_count += 1
            
    
    present_percentage = (present_count / len(attendance_list)) * 100
    
    
    
    return render_template('student.html',
                           student=student,
                           attendance_list=attendance_list,
                           present_percentage=present_percentage,
                           attendance_days=attendance_days,
                           exams=exams)




@views.route('/attendance_batch/<int:class_id>', methods=['POST'])
def attendance_batch(class_id):
    students = db_session.query(Students).filter_by(class_id=class_id).all()
    today_date = datetime.now().date()
    for student in students:
        attendance_status = request.form.get(f'attendance_{student.id}')
        if attendance_status in ['present', 'absent']:  
            existing_attendance = db_session.query(Attendance).filter_by(
                student_id=student.id, date=str(today_date)
            ).first()

            if existing_attendance:
                existing_attendance.status = attendance_status
            else:
                new_attendance = Attendance(
                    student_id=student.id,
                    class_id=class_id,
                    date=str(today_date),  
                    status=attendance_status
                )
                db_session.add(new_attendance)

    db_session.commit()
    flash('Attendance saved successfully for the class!', 'success')
    return redirect(url_for('views.show_class', class_id=class_id))



@views.route('/notifications', methods=['POST','GET'])
def notifications():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        date = request.form.get('date')
        teacher_id = request.form.get('teacher_id')

        

    # Create the notification
        new_notification = Notifications(
            title=title,
            content=content,
            date=date,
            teacher_id=teacher_id
        )

    # Save to the database
        db_session.add(new_notification)
        db_session.commit()

        flash("Notification sent successfully!", "success")
        return redirect(url_for('views.notifications'))
    return render_template('admin/dashboard.html')



@views.route('/attendance_page/<int:teacher_id>')
def attendance_page(teacher_id):
    # Overall attendance percentage calculation
    attendance_list = db_session.query(Attendance).all()
    total_attendance = len(attendance_list)
    present_count = sum(1 for attendance in attendance_list if attendance.status == 'present')
    attendance_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0

    # Daily attendance summary
    daily_attendance = defaultdict(lambda: {"present": 0, "absent": 0})
    for attendance in attendance_list:
        date_obj = (
            datetime.strptime(attendance.date, '%Y-%m-%d').date()
            if isinstance(attendance.date, str) else attendance.date
        )
        date_str = date_obj.strftime('%Y-%m-%d')
        daily_attendance[date_str][attendance.status.lower()] += 1

    chart_data = [["Date", "Present", "Absent"]]
    for date, counts in sorted(daily_attendance.items()):
        chart_data.append([date, counts['present'], counts['absent']])

    # Class-wise attendance with percentages
    class_wise_attendance = db_session.query(
        Class.name.label("class_name"),
        Class.id.label("class_id"),
        Teacher.id.label("teacher_id"),
        func.group_concat(Students.first_name).label("student_names"),
        func.group_concat(Attendance.status).label("attendance_statuses")
    ).join(
        Teacher, Class.teacher_id == Teacher.id
    ).join(
        Students, Students.class_id == Class.id
    ).join(
        Attendance, Attendance.student_id == Students.id
    ).filter(
        Teacher.id == teacher_id
    ).group_by(
        Class.name, Class.id, Teacher.id
    ).all()

    class_attendance_with_percentage = []
    for cls in class_wise_attendance:
        attendance_statuses = cls.attendance_statuses.split(',')
        present_count = sum(1 for status in attendance_statuses if status.strip().lower() == 'present')
        attendance_percentage = round((present_count / len(attendance_statuses)) * 100, 2) if attendance_statuses else 0
        class_attendance_with_percentage.append({
            "class_name": cls.class_name,
            "class_id": cls.class_id,
            "teacher_id": cls.teacher_id,
            "student_names": cls.student_names.split(','),
            "attendance_percentage": attendance_percentage
        })

    # Student-wise attendance and percentages
    class_ids = db_session.query(Class.id).all()
    student_wise_attendance = {}
    students_attendance_percentage = {}

    for class_id in class_ids:
        id = class_id[0]
        # Attendance details for students in each class
        attendance_data = db_session.query(
            Students.first_name,
            Students.last_name,
            Class.name,
            Attendance.status
        ).join(
            Attendance, Students.id == Attendance.student_id
        ).join(
            Class, Class.id == Attendance.class_id
        ).filter(
            Attendance.class_id == id,
            Attendance.date == datetime.now().date()
        ).all()

        class_name = attendance_data[0][2] if attendance_data else f"Class {id}"

        student_wise_attendance[class_name] = [
            {
                'first_name': row[0],
                'last_name': row[1],
                'attendance_status': row[3]
            } for row in attendance_data
        ]

        # Attendance percentage per student in the class
        students_percentage = db_session.query(
            Students.first_name,
            Students.last_name,
            (func.sum(case((Attendance.status == 'present', 1), else_=0)) * 100.0 / func.count(Attendance.status)).label('attendance_percentage')
        ).join(
            Attendance, Students.id == Attendance.student_id
        ).join(
            Class, Attendance.class_id == Class.id
        ).filter(
            Class.id == id
        ).group_by(
            Students.id
        ).all()

        students_attendance_percentage[class_name] = [
            {
                'first_name': row[0],
                'last_name': row[1],
                'attendance_percentage': row[2]
            } for row in students_percentage
        ]
   
    
    
    

    return render_template(
        'attendance_page.html',
        attendance_percentage=attendance_percentage,
        chart_data=chart_data,
        class_attendance_with_percentage=class_attendance_with_percentage,
        student_wise_attendance=student_wise_attendance,
        students_attendance_percentage=students_attendance_percentage
    )







@views.route('/marks/<int:student_id>', methods=["GET", "POST"])
def marks(student_id):
    current_date = datetime.now().date()
    student = db_session.query(Students).filter(Students.id == student_id).first()
    subjects = db_session.query(Subjects).all()
    all_exams = db_session.query(Exams).all()

    upcoming_exams = db_session.query(Exams).filter(Exams.date >= datetime.now()).all()

    past_exams = db_session.query(Exams).filter(Exams.date < datetime.now().time()).all()

    past_exams_without_marks = db_session.query(Exams).outerjoin(Marks, Marks.exam_id == Exams.id) \
        .filter(Exams.date < current_date, Marks.exam_id == None).all()

    ongoing_exams = db_session.query(Exams).filter(
        func.str_to_date(func.substring_index(Exams.time, ' - ', 1), '%I:%i %p') <= func.curtime(),
        func.str_to_date(func.substring_index(Exams.time, ' - ', -1), '%I:%i %p') >= func.curtime()
    ).all()

    marks_for_student = db_session.query(Marks).filter(Marks.student_id == student_id).all()

    if request.method == "POST":
        for subject in subjects:
            for exam in all_exams:
                marks_key = f"marks_{subject.id}_{exam.id}"
                if marks_key in request.form:
                    marks_value = request.form[marks_key]
                    if marks_value:
                        existing_mark = db_session.query(Marks).filter(Marks.student_id == student_id, Marks.exam_id == exam.id, Marks.subject_id == subject.id).first()
                        if existing_mark:
                            existing_mark.marks = marks_value
                        else:
                            new_mark = Marks(
                                student_id=student_id,
                                exam_id=exam.id,
                                subject_id=subject.id,
                                marks=marks_value
                            )
                            db_session.add(new_mark)
        db_session.commit()

    return render_template(
        'marks.html',
        student=student,
        exams=all_exams,
        subjects=subjects,
        marks=marks_for_student,
        upcoming_exams=upcoming_exams,
        past_exams=past_exams,
        ongoing_exams=ongoing_exams,
        past_exams_without_marks=past_exams_without_marks
    )




@views.route('/add_marks/<int:student_id>', methods=['POST'])
def add_marks(student_id):
    student = db_session.query(Students).filter(Students.id == student_id).first()
    exams = db_session.query(Exams).filter(Exams.date <= datetime.today()).all()
    subjects = db_session.query(Subjects).all()
    
    # Iterate through the form data to get marks
    for subject in subjects:
        for exam in exams:
            marks_key = f"marks_{subject.id}_{exam.id}"
            marks_value = request.form.get(marks_key)
            if marks_value:
                # Save the marks in the database, you might need to adapt this to your Marks model
                mark = Marks(student_id=student.id, subject_id=subject.id, exam_id=exam.id, marks=marks_value)
                db_session.add(mark)
    
    db_session.commit()
    return redirect(url_for('views.dashboard'))


@views.route('/performance/<int:teacher_id>')
def performance(teacher_id):
    classes = db_session.query(Class).filter(Class.teacher_id == teacher_id).all()
    
    subjects = db_session.query(Subjects).filter(Subjects.teacher_id == teacher_id).all()
    
    
    
    
    data = zip(classes,subjects)
    return render_template('performance.html',data=data)

    










