from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    assignments = db.relationship('Assignments', backref='author', lazy=True)
    labs = db.relationship('Labs', backref='author', lazy=True)
    exam = db.relationship('Exam', backref='author', lazy=True)
    remark = db.relationship('Remark', backref='author', lazy=True)
    feedback = db.relationship('Feedback', backref='author', lazy=True)

    def __repr__(self):
        return f"Person('{self.username}', '{self.role}')"

class Assignments(db.Model):
    __tablename__ = 'Assignments'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    assignment_number = db.Column(db.Integer, nullable=False)
    mark = db.Column(db.Integer, nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable = False)

    def __repr__(self):
        return f"Assignments('{self.username}', '{self.assignment_number}', '{self.mark}')"

class Labs(db.Model):
    __tablename__ = 'Labs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    lab_number = db.Column(db.Integer, nullable=False)
    mark = db.Column(db.Integer, nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable = False)

    def __repr__(self):
        return f"Labs('{self.username}', '{self.lab_number}', '{self.mark}')"

class Exam(db.Model):
    __tablename__ = 'Exam'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    mark = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable = False)

    def __repr__(self):
        return f"Exam('{self.username}', '{self.type}', '{self.mark}')"

class Remark(db.Model):
    __tablename__ = 'Remark'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    type_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(50), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable = False)

    def __repr__(self):
        return f"Remark('{self.username}', '{self.category}', '{self.type_number}', '{self.description}')"

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    answer_one = db.Column(db.String(50), nullable=False)
    answer_two = db.Column(db.String(50), nullable=False)
    answer_three = db.Column(db.String(50), nullable=False)
    answer_four = db.Column(db.String(50), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable = False)

    def __repr__(self):
        return f"Remark('{self.username}', '{self.answer_one}', '{self.answer_two}', '{self.answer_three}', '{self.answer_four}')"    

@app.route('/', methods = ['GET', 'POST'])
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        hashed_password = bcrypt.generate_password_hash(request.form['Password']).decode('utf-8')
        user_details = (request.form['Username'], hashed_password, request.form['Role'])
        add_users(user_details)
        return render_template('login.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['Username']
        password = request.form['Password']
        query_users = Users.query.all()
        for result in query_users:
            if result.username == username and bcrypt.check_password_hash(result.password, password):
                if result.role == "student":
                    return render_template('studentcontents.html', username = username)
                else:
                    return render_template('instructorcontents.html', username = username)
        flash('Incorrect username/password', 'error')
        return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/lectures')
def lectures():
    return render_template('lectures.html')

@app.route('/labs')
def labs():
    return render_template('labs.html')

@app.route('/assignments')
def assignments():
    return render_template('assignments.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/courseteam')
def courseteam():
    return render_template('courseteam.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/studentgrades/<string:username>')
def studentgrades(username):
    return render_template('studentgrades.html', username = username)

@app.route('/studentassignments/<string:username>', methods = ['GET', 'POST'])
def studentassignments(username):
    if request.method == 'GET':
        users_assignment_result = query_users_assignment(username)
        return render_template('studentassignments.html', username = username, users_assignment_result = users_assignment_result)
    else:
        description = request.form['RemarkRequest']
        type_number = request.form['AssignmentNumber']
        users_id = query_users_id(username)
        add_remark_request(username, "Assignment", type_number, description, users_id)
        return render_template('studentcontents.html', username = username)

@app.route('/studentlabs/<string:username>', methods = ['GET', 'POST'])
def studentlabs(username):
    if request.method == 'GET':
        users_lab_result = query_users_lab(username)
        return render_template('studentlabs.html', username = username, users_lab_result = users_lab_result)
    else:
        description = request.form['RemarkRequest']
        type_number = request.form['LabNumber']
        users_id = query_users_id(username)
        add_remark_request(username, "Lab", type_number, description, users_id)
        return render_template('studentcontents.html', username = username)

@app.route('/studentexams/<string:username>', methods = ['GET', 'POST'])
def studentexams(username):
    if request.method == 'GET':
        users_exam_result = query_users_exam(username)
        return render_template('studentexams.html', username = username, users_exam_result = users_exam_result)
    else:
        description = request.form['RemarkRequest']
        category = request.form['ExamType']
        users_id = query_users_id(username)
        add_remark_request(username, category, 0, description, users_id)
        return render_template('studentcontents.html', username = username)

@app.route('/studentfeedback/<string:username>', methods = ['GET', 'POST'])
def studentfeedback(username):
    if request.method == 'GET':
        users_instructor_result = query_instructor()
        return render_template('studentfeedback.html', username=username, users_instructor_result = users_instructor_result)
    else:
        instructor_username = request.form['SelectInstructor']
        answer_one = request.form['likeTeaching']
        answer_two = request.form['improveTeaching']
        answer_three = request.form['likeLabs']
        answer_four = request.form['improveLabs']
        users_id = query_users_id(username)
        add_feedback(instructor_username, answer_one, answer_two, answer_three, answer_four, users_id)
        return render_template('studentcontents.html', username = username)

@app.route('/instructorgrades/<string:username>')
def instructorgrades(username):
    return render_template('instructorgrades.html', username = username)

@app.route('/instructorassignments/<string:username>', methods = ['GET', 'POST'])
def instructorassignments(username):
    users_assignment_result = Assignments.query.all()
    return render_template('instructorassignments.html', username = username, users_assignment_result = users_assignment_result)

@app.route('/instructorlabs/<string:username>', methods = ['GET', 'POST'])
def instructorlabs(username):
    users_lab_result = Labs.query.all()
    return render_template('instructorlabs.html', username = username, users_lab_result = users_lab_result)

@app.route('/instructorexams/<string:username>', methods = ['GET', 'POST'])
def instructorexams(username):
    if request.method == 'GET':
        users_exam_result = Exam.query.all()
        return render_template('instructorexams.html', username = username, users_exam_result = users_exam_result)

@app.route('/instructorfeedback/<string:username>', methods = ['GET', 'POST'])
def instructorfeedback(username):
    users_feedback_result = query_users_feedback(username)
    return render_template('instructorfeedback.html', username = username, users_feedback_result = users_feedback_result)

@app.route('/instructorremark/<string:username>', methods = ['GET', 'POST'])
def instructorremark(username):
    users_remark_result = Remark.query.all()
    return render_template('instructorremark.html', username = username, users_remark_result = users_remark_result)

@app.route('/instructormark/<string:username>', methods = ['GET', 'POST'])
def instructormark(username):
    if request.method == 'GET':
        users_student_result = query_student()
        return render_template('instructormark.html', username = username, users_student_result = users_student_result)
    else:
        student_username = request.form['SelectStudent']
        category = request.form['Category']
        number = request.form['Number']
        grade = request.form['EnterGrade']
        users_id = query_users_id(username)
        add_student_mark(student_username, category, number, grade, users_id)
        return render_template('instructorcontents.html', username = username)

def add_users(user_details):
    user = Users(username = user_details[0], password = user_details[1], role = user_details[2])
    db.session.add(user)
    db.session.commit()

def query_users_assignment(username):
    query_assignments = Assignments.query.all()
    users_assignment_result = []
    for assignments in query_assignments:
        if assignments.username == username:
            users_assignment_result.append(assignments)
    return users_assignment_result

def query_users_id(username):
    query_users = Users.query.all()
    for users in query_users:
        if users.username == username:
            return users.id

def add_remark_request(username, category, type_number, description, users_id):
    remark_request = Remark(username=username, category=category, type_number=type_number, description=description, users_id=users_id)
    db.session.add(remark_request)
    db.session.commit()

def query_users_lab(username):
    query_labs = Labs.query.all()
    users_lab_result = []
    for lab in query_labs:
        if lab.username == username:
            users_lab_result.append(lab)
    return users_lab_result

def query_users_exam(username):
    query_exams = Exam.query.all()
    users_exam_result = []
    for exam in query_exams:
        if exam.username == username:
            users_exam_result.append(exam)
    return users_exam_result

def query_instructor():
    query_users = Users.query.all()
    users_instructor_result = []
    for user in query_users:
        if user.role == "instructor":
            users_instructor_result.append(user.username)
    return users_instructor_result

def add_feedback(username, answer_one, answer_two, answer_three, answer_four, users_id):
    feedback = Feedback(username=username, answer_one=answer_one, answer_two=answer_two, answer_three=answer_three, answer_four=answer_four, users_id=users_id)
    db.session.add(feedback)
    db.session.commit()

def query_users_feedback(username):
    query_feedback = Feedback.query.all()
    users_feedback_result = []
    for feedback in query_feedback:
        if feedback.username == username:
            users_feedback_result.append(feedback)
    return users_feedback_result

def query_student():
    query_users = Users.query.all()
    users_student_result = []
    for user in query_users:
        if user.role == "student":
            users_student_result.append(user.username)
    return users_student_result

def add_student_mark(username, category, number, grade, users_id):
    if category == "Assignment":
        assignment = Assignments(username=username, assignment_number=number, mark=grade, users_id=users_id)
        db.session.add(assignment)
        db.session.commit()
    elif category == "Lab":
        lab = Labs(username=username, lab_number=number, mark=grade, users_id=users_id)
        db.session.add(lab)
        db.session.commit()
    else:
        exam = Exam(username=username, mark=grade, type=category, users_id=users_id)
        db.session.add(exam)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)