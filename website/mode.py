from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# Admin Model
class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    password = Column(String)

    def set_password(self, password):
        self.password = password


# Teacher Model
class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    notifications = relationship("Notifications", back_populates="teacher", cascade="all, delete-orphan")
    classes = relationship("Class", back_populates="teacher", cascade="all, delete-orphan")
    additional_information = relationship(
        "Additional_Information", back_populates="teacher", uselist=False, cascade="all, delete-orphan"
    )
    subjects = relationship("Subjects", back_populates="teacher", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Teacher(id={self.id}, username={self.username}, email={self.email})>"


# Additional Information for Teacher
class Additional_Information(Base):
    __tablename__ = 'additional_information'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    phone = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    subject = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    teacher = relationship("Teacher", back_populates="additional_information")

    def __repr__(self):
        return f"<Additional_Information(id={self.id}, phone={self.phone}, address={self.address})>"


# Class Model
class Class(Base):
    __tablename__ = 'classes'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, onupdate=datetime.utcnow)

    teacher = relationship("Teacher", back_populates="classes")
    # One-to-many relationship: a Class can have multiple Subjects
    subjects = relationship("Subjects", back_populates="class_assigned", cascade="all, delete-orphan")
    students = relationship('Students', back_populates='class_assigned', cascade="all, delete-orphan")
    attendance_records = relationship('Attendance', back_populates='class_details', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Class(id={self.id}, name={self.name}, teacher_id={self.teacher_id})>"






# Student Model
class Students(Base):
    __tablename__ = 'students'

    id = Column(Integer, autoincrement=True, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    
    class_assigned = relationship('Class', back_populates='students')
    attendance_records = relationship('Attendance', back_populates='student', cascade="all, delete-orphan")
    marks = relationship('Marks', back_populates='student', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Student(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email})>"


# Subjects Model
class Subjects(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=True)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=True)  # ForeignKey for class assignment
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    teacher = relationship('Teacher', back_populates='subjects')
    # Many-to-one relationship: Subjects belong to a specific Class
    class_assigned = relationship('Class', back_populates='subjects')
    marks = relationship('Marks', back_populates='subject', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subjects(id={self.id}, name={self.name}, code={self.code})>"






# Attendance Model
class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    date = Column(String, nullable=False)
    status = Column(String, nullable=False)
    

    student = relationship("Students", back_populates="attendance_records")
    class_details = relationship("Class", back_populates="attendance_records")

    def __repr__(self):
        return f"<Attendance(id={self.id}, student_id={self.student_id}, class_id={self.class_id}, date={self.date}, status={self.status})>"


# Exams Model
class Exams(Base):
    __tablename__ = 'exams'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    date = Column(String, nullable=True)
    time = Column(String, nullable=True)

    marks = relationship('Marks', back_populates='exam', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Exams(id={self.id}, name={self.name}, date={self.date}, time={self.time})>"


# Marks Model
class Marks(Base):
    __tablename__ = 'marks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)  
    marks = Column(Integer, nullable=True)
    grade = Column(String, nullable=True)
    
    # Relationships
    student = relationship('Students', back_populates='marks')
    exam = relationship('Exams', back_populates='marks')
    subject = relationship('Subjects', back_populates='marks')

    def __repr__(self):
        return f"<Marks(id={self.id}, student_id={self.student_id}, exam_id={self.exam_id}, subject_id={self.subject_id}, marks={self.marks}, grade={self.grade})>"


# Events Model
class Events(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    location = Column(String, nullable=False)

    def __repr__(self):
        return f"<Events(id={self.id}, name={self.name}, description={self.description}, date={self.date}, time={self.time}, location={self.location})>"


# Notifications Model
class Notifications(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    date = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    
    teacher = relationship('Teacher', back_populates='notifications')

    def __repr__(self):
        return f"<Notifications(id={self.id}, title={self.title}, content={self.content}, date={self.date}, teacher_id={self.teacher_id})>"

# Create the engine and database schema
engine = create_engine('mysql+pymysql://root:shinu@localhost/teachers')
Base.metadata.create_all(engine)
