from pymongo import MongoClient

# Initializing Database
# Creating a pymongo client

client = MongoClient('localhost', 27017)

# Getting the database instance
db = client['evaluation']
print('Database Created')

# Creating a collection
students = db['students']
admins = db['admins']
lecturers = db['lecturers']

sessions = db['sessions']
levels = db['levels']
semesters = db['semesters']
positions = db['positions']
states = db['states']
courses = db['courses']

questions = db['questions']
announcements = db['announcements']
