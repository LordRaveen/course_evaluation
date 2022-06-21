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


def evaluation_duration(course):
    """calculates & returns the appropriate time to be spent in evaluating"""
    _questions = [question for question in questions.find({"course": course})]
    duration = len(_questions) * 15
    time = f"{duration} secs"

    if duration > 60:
        mins = int(duration / 60)
        mins_text = f"{mins} min" if mins == 1 else f"{mins} mins"
        secs = duration - (60 * mins)
        secs_text = "" if secs == 0 else f"{secs} secs"

        time = f"{mins_text} {secs_text} "

    return time

  

@views.route('/dashboard')
@is_logged_in
def dashboard():

    if session['usertype'] == 'student':
        account = students.find_one({"regnumber": session['regnumber']})

        query = [{"level": account['level']}, 
                 {"open_for_evaluation": 'true'}]

        courses_query = [course for course in courses.find({"$and": query})]
        courses_offered = [course for course in courses_query if course['course'] not in account['courses_evaluated']]

        courses_evaluated = [course for course in courses_query if course['course'] in account['courses_evaluated']]

        
        return render_template('dashboard.html', account=account,
                                courses_offered=courses_offered,
                                courses_evaluated=courses_evaluated,
                                evaluation_duration=evaluation_duration)
    
    elif session['usertype'] == 'lecturer':
        account = lecturers.find_one({"username": session['username']})
        courses_taught = [course_taught for course_taught in courses.find() if account['_id'] == ObjectId(course_taught['lecturer'])]
        
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
                            find_lecturer=find_lecturer,
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
 

@views.route('evaluation_result')
@is_admin
def evaluation_result():
    
    return render_template('admin/evaluation_result.html')


@views.route('/evaluation_stats', methods=['GET'])
@is_admin
def evaluation_stats():

    level_list = [ level for level in levels.find() ]
    data = {}

    for level in level_list:

        course_list = [ course for course in courses.find({"level": level['level']}) ]
        title = f"{level['class']} stats - BarChart"
        data100, data75, data50, data25, _course = [], [], [], [], []
        # def calc_per(total)

        calc_per = lambda total, single: float(f"{single / total * 100:.2f}")


        for course in course_list:

            x = course['scores']
            num100, num75, num50, num25 = x['100'] + 1, x['75'] + 1, x['50'] + 1, x['25'] + 1

            # accuired_score = sum([num100 * 100, num75 , num50, num25])
            # division error

            expected_score = sum([num100, num75, num50, num25])
            print(expected_score)

            data100.append( calc_per(expected_score, num100) )
            data75.append( calc_per(expected_score, num75) )
            data50.append( calc_per(expected_score, num50) )
            data25.append( calc_per(expected_score, num25) )
            _course.append(course['course'])

        data[f"level{level['level']}"] = {
                                "title": title,
                                "courses": _course,
                                "data100": data100, 
                                "data75": data75, 
                                "data50": data50, 
                                "data25": data25, 
                                }

    print(data, course_list)
    
    return jsonify(data)




    