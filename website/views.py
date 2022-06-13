from flask import Blueprint, render_template, jsonify, session, redirect, url_for, flash, request
from markupsafe import re
from .auth import is_logged_in, is_admin
import random
from .database import *
from bson.objectid import ObjectId


views = Blueprint('views', __name__)


@views.route('/api')
def api():
    c = random.random()
    return jsonify({'data': f'{c}'})


@views.route('/')
def index():
    return render_template('index.html')


@views.route('/dashboard')
@is_logged_in
def dashboard():

    if session['usertype'] == 'student':
        account = students.find_one({"regnumber": session['regnumber']})
        courses_offered = courses.find({"level": account['level']})
        
        return render_template('dashboard.html', account=account, courses_offered=courses_offered)
    
    elif session['usertype'] == 'lecturer':
        account = lecturers.find_one({"username": session['username']})
        courses_taught = [course_taught for course_taught in courses.find() if account['_id'] == ObjectId(course_taught['lecturer'])]
        print(account, courses_taught)
        return render_template('lecturer/lecturer_dashboard.html', courses_taught=courses_taught, questions=questions)

    elif session['usertype'] == 'admin':
        return render_template('admin/dashboard.html')

    else:
        flash('Sorry, You cannot access this page.')
        return redirect(url_for('auth.login'))


@views.route('/recover_password')
def recover_password():
    return render_template('recover_password.html')


@views.route('/profile')
@is_logged_in
def profile():
    collection = db[f"{session['usertype']}s"]
    user_found = collection.find_one({"regnumber": session["regnumber"]}) if session['usertype'] == 'student' else collection.find_one({"username": session["username"]})
    return render_template('profile.html', user_found=user_found)


@views.route('/settings')
@is_admin
def settings(): 
    data = {}
    data['sessions'] = [session for session in sessions.find()]
    data['levels'] = [level for level in levels.find()]
    data['semesters'] = [semester for semester in semesters.find()]
    data['positions'] = [position for position in positions.find()]
    data['states'] = [state for state in states.find()]
    print(data)
    return render_template('admin/settings.html', data=data)


@views.route('/manage_lecturers')
@is_admin
def manage_lecturers():
    lecturer = [lecturer for lecturer in lecturers.find()]
    position = [position for position in positions.find().sort('position')]
    return render_template('admin/manage_lecturers.html', lecturers=lecturer, positions=position)


def find_lecturer(id):
    """
        Returns a lecturer found
    """
    lecturer = lecturers.find_one({"_id": id})
    return lecturer if lecturer is not None else 'None'


@views.route('/manage_courses')
@is_admin
def manage_courses():
    lecturer_list = [lecturer for lecturer in lecturers.find()]
    level_list = [level for level in levels.find()]
    semester_list = [semester for semester in semesters.find()]
    course_list = [course for course in courses.find()]

    print(lecturer_list)
    return render_template('admin/manage_courses.html',
                            lecturers=lecturer_list,
                            levels=level_list,
                            semesters=semester_list,
                            courses=course_list,
                            ObjectId=ObjectId)


@views.route('/manage_students')
def manage_students():
    student_list = []
    studs = {}
    level_list = [level for level in levels.find()]

    for level in level_list:
        student_list = [student for student in students.find({'level': level['level']})]
        studs[f"{level['level']}"] = student_list
        student_list = []
    


    for stud in studs:
        print(f'{stud}:', studs[stud])

    

    return render_template('admin/manage_students.html', studs=studs, levels=level_list)


@views.route('/user/<id>')
def user(id): 
    return render_template('users.html', id=id)

@views.route('/evaluate/<string:id>')
@is_logged_in
def evaluate(id):
    course = courses.find_one({"course": id})
    student = students.find_one({"regnumber": session['regnumber']})

    if student['level'] != course['level']:
        flash("You have no business evaluating this course", 'warning')
        return redirect(url_for('views.dashboard'))

    if course['open_for_evaluation'] == 'false':
        flash(f"Course '{id}' is not open for evaluation", 'warning')
        return redirect(url_for('views.dashboard'))

    course_lecturer = lecturers.find_one({"_id": ObjectId(course['lecturer'])})
    question_list = [question for question in questions.find({"course": id, "activated": 'true'})]

    
    return render_template('evaluate.html', id=id, question_list=question_list, course=course,
                            course_lecturer=course_lecturer)
 
    