from re import L
from flask import Blueprint, render_template, session, request, flash, redirect, url_for, jsonify
from functools import wraps
from .database import *
import datetime
from bson.objectid import ObjectId
import random


dt = datetime.datetime.now()
date_now = dt.strftime('%A-%d-%b-%Y  %I:%M %p')

# Creating collection

auth = Blueprint('auth', __name__)


# Permission Decorator
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs): 
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else: 
            flash('Unauthorized Access!', 'danger')
            return redirect(url_for('auth.login'))
    return wrap


def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs): 
        if 'logged_in' in session:
            if session['usertype'] == 'admin':
                return f(*args, **kwargs)

            flash('Unauthorized Access! ❌', 'danger')
            return redirect(url_for('views.dashboard'))
        else: 
            flash('Unauthorized Access!', 'danger')
            return redirect(url_for('auth.login'))
    return wrap


def is_lecturer(f):
    @wraps(f)
    def wrap(*args, **kwargs): 
        if 'logged_in' in session:
            if session['usertype'] == 'lecturer' or session['usertype'] == 'admin':
                return f(*args, **kwargs)

            flash('Only a lecturer can access this page', 'danger')
            return redirect(url_for('views.dashboard'))
        else: 
            flash('Unauthorized Access!', 'danger')
            return redirect(url_for('auth.login'))
    return wrap



# ALL AUTHENTICATIONS ARE DONE HERE
@auth.route('/login', methods=['GET', 'POST'])
def login():

    if 'username' in session:
        flash('You are already logged in!', 'success')
        return redirect(url_for('views.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        account = students.find_one({"regnumber": username})
        lecturer_account = lecturers.find_one({"username": username})
        admin_account = admins.find_one({"username": username})
        print(admin_account)

        if account:
            print(account)
            if account['password'] == password:
                session['logged_in'] = True 
                session['username'] = account['firstname'] + " " + account['lastname']
                session['regnumber'] = account['regnumber']
                session['usertype'] = "student"
                return redirect(url_for('views.dashboard'))
            else: 
                flash('Invalid login details!', 'danger')
                return render_template('login.html')

        elif admin_account:
            if admin_account["password"] == password:
                session['logged_in'] = True
                session['username'] = username
                session['usertype'] = "admin"
                return redirect(url_for('views.dashboard'))
            else: 
                flash('Invalid login details!', 'danger')
                return render_template('login.html')


        elif lecturer_account:
            if lecturer_account["password"] == password:
                session['logged_in'] = True
                session['username'] = username
                session['usertype'] = "lecturer"
                return redirect(url_for('views.dashboard'))
            else:
                flash('Invalid login details', 'warning')
                return render_template('login.html')

        else: 
            flash('Account does not exists. Please Login', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@auth.route('/logout')
def logout(): 
    session.clear()
    flash('You are now logged out!', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        firstname = request.form.get('firstname').title()
        lastname = request.form.get('lastname').title()
        regnumber = request.form.get('regnumber').upper()
        phone = request.form.get('phone')
        email = request.form.get('email').lower()
        gender = request.form.get('gender').lower()
        level = request.form.get('level')
        pic = request.form.get('pic')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')


        try: # save to database
            if password == cpassword: 
                if students.find_one({"regnumber":regnumber}) or students.find_one({"phone":phone}) or students.find_one({"email":email}):
                    flash('Account exists!', 'danger')
                    return render_template('register.html')

                else:
                    student = {
                        'firstname': firstname, 
                        'lastname': lastname, 
                        'gender': gender, 
                        'regnumber': regnumber, 
                        'phone': phone, 
                        'email': email, 
                        'password': password,
                        'level': level,
                        'pic': pic,
                        'about': '',
                        'date_created': date_now}

                    students.insert_one(student)
                                                    
                    flash('Account created', 'success')
                    return render_template('register.html')
            
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')

        except Exception as e: 
            flash('Something went wrong. Please try again.', 'danger')
            return render_template('register.html')

    return render_template('register.html')


@auth.route('/add_student', methods=['POST'])
def add_student():

    if request.method == 'POST':
        firstname = request.form.get('firstname').title()
        lastname = request.form.get('lastname').title()
        regnumber = request.form.get('regnumber').upper()
        phone = request.form.get('phone')
        email = request.form.get('email').lower()
        gender = request.form.get('gender').lower()
        level = request.form.get('level')
        pic = request.form.get('pic')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')


        try: # save to database
            if password == cpassword: 
                if students.find_one({"regnumber":regnumber}) or students.find_one({"phone":phone}) or students.find_one({"email":email}):
                    flash('Account exists!', 'danger')
                    return redirect(url_for('views.manage_students'))

                else:
                    student = {
                        'firstname': firstname, 
                        'lastname': lastname, 
                        'gender': gender, 
                        'regnumber': regnumber, 
                        'phone': phone, 
                        'email': email, 
                        'password': password,
                        'level': level,
                        'pic': pic,
                        'about': '',
                        'date_created': date_now, 
                        'courses_evaluated':[]}

                    students.insert_one(student)
                                                    
                    flash('Account created!', 'success')
                    return redirect(url_for('views.manage_students'))
            
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('views.manage_students'))

        except Exception as e: 
            flash('Something went wrong. Please try again.', 'danger')
            return redirect(url_for('views.manage_students'))

    return redirect(url_for('views.manage_students'))


@auth.route('/update_student', methods=['GET', 'POST'])
def update_student():
    if request.method == 'POST':

        _id = request.form.get('_id')
        firstname = request.form.get('firstname').title()
        lastname = request.form.get('lastname').title()
        regnumber = request.form.get('regnumber').upper()
        phone = request.form.get('phone')
        email = request.form.get('email').lower()
        level = request.form.get('level')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')

        candidate = students.find_one({"_id": ObjectId(_id)})

        try:
            if password == cpassword:
                students.update_one(
                    {"_id": ObjectId(_id)},[
                    {"$set": {"regnumber": regnumber}},
                    {"$set": {"firstname": firstname}},
                    {"$set": {"lastname": lastname}},
                    {"$set": {"email": email}},
                    {"$set": {"phone": phone}},
                    {"$set": {"level": level}},
                    {"$set": {"password": password}},
                    {"$set": {"date_last_updated": date_now}}]
                )
                flash('Student Record Updated!', 'success')
                return redirect(url_for('views.manage_students'))

            flash('Passwords have to be the same', 'danger')
            return redirect(url_for('views.manage_students'))

        except:
            flash('An error occurred! Please try again later.', 'danger')
            return redirect(url_for('views.manage_students'))

    return redirect(url_for('views.manage_students'))


@auth.route('/update_profile', methods=['POST'])
@is_logged_in
def update_profile():
    if request.method == 'POST':
        username = request.form.get('username').lower()
        firstname = request.form.get('firstname').lower()
        lastname = request.form.get('lastname').lower()
        email = request.form.get('email').lower()
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        about = request.form.get('about').capitalize().strip()


        audience = db[f'{session["usertype"]}s']
        titles = "regnumber" if session["usertype"] == "student" else "username"
        candidate = audience.find_one({titles: session['username']})

        try: 
            audience.update_one(
            {titles:session['username']},[
            {"$set":{titles: username}},
            {"$set":{"firstname": firstname}},
            {"$set":{"lastname": lastname}},
            {"$set":{"email": email}},
            {"$set":{"phone": phone}},
            {"$set":{"gender": gender}},
            {"$set":{"about": about}},
            {"$set":{"date_last_updated": date_now}}])
            
            flash('Profile Updated!', 'success')
            return redirect(url_for('views.profile'))

        except Exception as e:
            flash('profile not saved', 'danger') 
            return render_template('profile.html')

    return render_template('profile.html')


@auth.route('/update_password', methods=['POST'])
@is_logged_in
def update_password():
    old_password = request.form.get('opassword')
    new_password = request.form.get('npassword')
    confirm_new_password = request.form.get('cnpassword')

    audience = db[f'{session["usertype"]}s']
    titles = "regnumber" if session["usertype"] == "student" else "username"

    candidate = audience.find_one({titles: session['username']})
    
    if candidate['password'] != old_password:
        flash("Old password is incorrect!", "danger")
        return redirect(url_for('views.profile'))
        
    if new_password == old_password:
        flash("Do not use your old password!", "danger")
        return redirect(url_for('views.profile'))

    if new_password != confirm_new_password:
        flash("New passwords do not match!", "danger")
        return redirect(url_for('views.profile'))

    audience.update_one({titles: session['username']},
                        {"$set": {"password": new_password}})
    flash("New password set!", "success")
    return redirect(url_for('views.profile'))
            

@auth.route('/add_setting', methods=['POST'])
@is_admin
def add_setting():
    if request.method == 'POST':
        item = request.form.get('item')
        collection = request.form.get('collection')
        field = request.form.get('field')

        try: 
            if db[collection].find_one({field: item}):
                flash(f'{field.title()} already exists!', 'danger')
                return  redirect(url_for('views.settings'))
            
            else:
                if field == 'level':
                    item2 = request.form.get('item2').upper()
                    db[collection].insert_one({field: item, "class": item2})

                else:
                    db[collection].insert_one({field: item})
                    flash(f'{field.title()} added!', 'success')
                    return  redirect(url_for('views.settings'))

            
        except:
            flash('An error occured! ', 'warning')
            return  redirect(url_for('views.settings'))
    return redirect(url_for('views.settings'))


@auth.route('/add_lecturer', methods=['GET', 'POST'])
@is_admin
def add_lecturer():
    if request.method == 'POST': 
        firstname = request.form.get('firstname').title()
        lastname = request.form.get('lastname').title()
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        position = request.form.get('position')
        password = request.form.get('password')
        date_created = date_now

        if position != 'none': 

            if lecturers.find_one({"username":username}) or lecturers.find_one({"phone":phone}) or lecturers.find_one({"email":email}):
                flash('Account exists!', 'danger')
                return redirect(url_for('views.manage_lecturers'))

            lecturer = {
                'firstname': firstname,
                'lastname': lastname,
                'username': username,
                'phone': phone,
                'email': email,
                'gender': '',
                'position': position,
                'password': password,
                'about': "",
                'date_created': date_created
            }
            lecturers.insert_one(lecturer)

            flash('Lecturer Added!', 'success')
            return redirect(url_for('views.manage_lecturers'))
        else: 
            flash('Please select a position', 'danger')
            return redirect(url_for('views.manage_lecturers'))
            pass
    return redirect(url_for('views.manage_lecturers'))


@auth.route('/update_lecturers', methods=[ 'POST'])
def update_lecturer():
    if request.method == 'POST':
        _id = request.form.get('_id')
        firstname = request.form.get('firstname').title()
        lastname = request.form.get('lastname').title()
        username = request.form.get('username').upper()
        phone = request.form.get('phone')
        email = request.form.get('email').lower()
        position = request.form.get('position')
        password = request.form.get('password')

        try:
            lecturers.update_one(
                {"_id": ObjectId(_id)},[
                {"$set": {"username": username}},
                {"$set": {"firstname": firstname}},
                {"$set": {"lastname": lastname}},
                {"$set": {"email": email}},
                {"$set": {"phone": phone}},
                {"$set": {"position": position}},
                {"$set": {"password": password}},
                {"$set": {"date_last_updated": date_now}}]
            )
            flash('Lecturer Record Updated!', 'success')
            return redirect(url_for('views.manage_lecturers'))
        except:
            flash('An error occurred! Please try again.', 'danger')
            return redirect(url_for('views.manage_lecturers'))


@auth.route('/add_course', methods=['POST'])
@is_admin
def add_course():
    if request.method == 'POST':

        course = request.form.get('course')
        code = request.form.get('code').upper()
        credit_unit = request.form.get('credit_unit')
        level = request.form.get('level')
        semester = request.form.get('semester')
        lecturer = request.form.get('lecturer')

        if courses.find_one({"course":course}) or courses.find_one({"code":code}):
            flash('Account exists!', 'danger')
            return redirect(url_for('views.manage_lecturers'))

        course = {
            'course':course,
            'code':code,
            'credit_unit': credit_unit,
            'level': level,
            'semester': semester,
            'lecturer': lecturer,
            'open_for_evaluation': 'false',
            'scores': {'100': 0, '75': 0, '50': 0, '25': 0, 
                       'total': 0, 'percent': 0, 'no_of_evaluation': 0}
        }

        courses.insert_one(course)
        flash('Course has been added!', 'success')

    return redirect(url_for('views.manage_courses'))


@auth.route('/update_course', methods=['POST'])
def update_course():
    if request.method == 'POST':
        _id = request.form.get('_id')
        course = request.form.get('course')
        code = request.form.get('code')
        credit_unit = request.form.get('credit_unit')
        level = request.form.get('level')
        semester = request.form.get('semester')
        lecturer = request.form.get('lecturer')

        try:
            courses.update_one(
                {"_id": ObjectId(_id)},[
                {"$set": {"course": course}},
                {"$set": {"code": code}},
                {"$set": {"credit_unit": credit_unit}},
                {"$set": {"level": level}},
                {"$set": {"semester": semester}},
                {"$set": {"lecturer": lecturer}},
                {"$set": {"date_last_updated": date_now}}]
            )
            flash('Course Record Updated!', 'success')
            return redirect(url_for('views.manage_courses'))

        except:

            flash('An error occured! Please try again.', 'danger')
            return redirect(url_for('views.manage_courses'))


@auth.route('/delete', methods=['POST'])
@is_lecturer
def delete():
    _id = request.form.get('_id')
    page = request.form.get('page')
    collection = request.form.get('collection')
    item = collection[:-1].title()

    try:
        db[collection].delete_one({"_id": ObjectId(_id)})
        flash(f'{item} Deleted!', 'success')
    except:
        flash('An error occured! ', 'warning')
    return  redirect(url_for(page))


@auth.route('/add_question', methods=['POST'])
def add_question():
    if request.method == 'POST':
        course = request.form.get('course')
        question = request.form.get('question')
        option_type = request.form.get('option_type')

        if option_type == 'good':
            db_option_type = {"Very good": 100, "Good": 75, "Average": 50, "Poor":25}

        elif option_type == 'likely':
            db_option_type = {"More likely": 100, "Likely": 75, "Unlikely": 50, "More unlikely":25}

        else:
            db_option_type = {"Strongly agree": 100, "Agree": 75, "Disagree": 50, "Strongly disagree":25}


        if questions.find_one({"question": question, "course": course}) == None:
            questions.insert_one({"question": question,
                                  "course": course,
                                  "option_type": option_type,
                                  "options": db_option_type,
                                  "activated" : "true",
                                  "date_created": date_now})

            flash('Question Added', 'success')
        else:
            flash('Question Exists', 'danger')
        
    return redirect(url_for('views.dashboard'))


@auth.route('/activate', methods=["POST"])
@is_lecturer
def activate():
    question_id = request.form.get('question_id')
    page = request.form.get('page')

    if request.method == 'POST':
        questions.update_one({"_id": ObjectId(question_id)},
                            {"$set": {"activated" : 'true'}})

        flash('Question Activated', 'success')
        return redirect(url_for(page))


@auth.route('/deactivate', methods=["POST"])
@is_lecturer
def deactivate():
    question_id = request.form.get('question_id')
    page = request.form.get('page')

    if request.method == 'POST':
        questions.update_one({"_id": ObjectId(question_id)},
                            {"$set": {"activated" : 'false'}})

        flash('Question Activated', 'success')

        return redirect(url_for(page))


@auth.route('activate_evaluation/<string:id>', methods=['POST'])
def activate_evaluation(id):
    link = url_for('views.dashboard')
    if request.method == 'POST':
        if request.form.get('method') == 'activate':
            courses.update_one({"_id": ObjectId(id)}, {"$set": {"open_for_evaluation": 'true'}}) 
            flash('Course Evaluation Activated', 'success')

        else:
            courses.update_one({"_id": ObjectId(id)}, {"$set": {"open_for_evaluation": 'false'}})
            flash('Course Evaluation Deactivated', 'success')

    return redirect(link)


@auth.route('/evaluation_sum', methods=['POST'])
def evaluation_sum():

    if request.method == 'POST':

        course = request.form.get('course')

        # get the list of questions answered
        feedback = [item for item in request.form.items()][1:]
        no_questions_answered = len(feedback)

        # send individual score to db.courses.scores
        for score in feedback:
            evaluated_course = courses.find_one({'course': course})

            possible_score = [100, 75, 50, 25]


            for i in possible_score:
                if int(score[1]) == i:
                    courses.update_one({"course": course},
                                    {'$set': {f"scores.{score[1]}": evaluated_course['scores'][f'{score[1]}'] + 1} })
            
            # if int(score[1]) == 75:
            #     courses.update_one({"course": course},
            #                        {'$set': {f"scores.{score[1]}": evaluated_course['scores'][f'{score[1]}'] + 1} })
            
            # if int(score[1]) == 50:
            #     courses.update_one({"course": course},
            #                        {'$set': {f"scores.{score[1]}": evaluated_course['scores'][f'{score[1]}'] + 1} })
            
            # if int(score[1]) == 25:
                # courses.update_one({"course": course},
                #                    {'$set': {f"scores.{score[1]}": evaluated_course['scores'][f'{score[1]}'] + 1} })
        
        # calculate total in percentage score after each evaluation
        # add up the scores
        total_score = 0
        percentage = 0
        scores = lambda x: courses.find_one({"course": course})['scores'][x]    

        for i in feedback:
            total_score += int(i[1])

        # percentage = total_score / ( no_questions_answered * 100 ) * 100

        # increment the total in db
        courses.update_one({"course": course}, {'$set': {f"scores.total": scores('total') + total_score} })

        # increment number of evaluations by 1
        courses.update_one({"course": course}, {'$set': {f"scores.no_of_evaluation": scores('no_of_evaluation') + 1} })


        # recalculate the average percentage in db
        no_of_eval = 1 if scores('no_of_evaluation') <= 0 else scores('no_of_evaluation')
        sum_scores = sum([scores('25'), scores('50'), scores('75'), scores('100')] )
        db_total = courses.find_one({'course': course})['scores']['total']
        
        new_percentage_raw = ( db_total / (sum_scores * 100) ) * 100
        new_percentage = round(new_percentage_raw)

        courses.update_one({"course": course}, {'$set': {f"scores.percent": new_percentage} })
        students.update_one({"regnumber": session['regnumber']},
                             {'$push': {'courses_evaluated': course}})

        flash('Evaluation Successful!', 'success')
    return redirect(url_for('views.dashboard'))



#####################
@auth.route('/test')
def test():
    return render_template('test.html')

@auth.route('tester')
def tester():
    student_data = courses.find()
    return render_template('_test.html', student_data=student_data)