from flask import Flask, request, jsonify
# from flask_pymongo import pymongo
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
# app.config['CORS_HEADERS'] = 'Content-Type'





# generate a hexa decimal secret key assign to variable secret

secret = 'bjefisdhbiesudbv4545njk3b2b4ejwb343nkbn3jkb43b' 
app.config['JWT_SECRET_KEY'] = secret
jwt = JWTManager(app)
# connect to MongoDB
mongo=MongoClient('mongodb://localhost:27017/')
db = mongo['jobportal']

users = db['users']
jobs = db['jobs']
class User():
    def __init__(self,name, username, email, password, role):
        self.name = name
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.role = role
class Job():
    def __init__(self, title, description, location, mobile):
        self.title = title
        self.description = description
        self.location = location
        self.mobile = mobile


@app.route('/api/register', methods=['POST'])
@cross_origin()
def register():
    data = request.get_json()
    print(data)
    name = data['name']
    username = data['username']
    email = data['email']
    password = data['password']
    role = data['role']
    user = users.find_one({'email': email})
    if user:
        return jsonify({'message': 'User already exists'})
    new_user = User(name,username, email, password, role)
    users.insert_one(new_user.__dict__)
    access_token = create_access_token(identity=email)
    # add headers to response
    response = jsonify({'message': 'User created successfully', 'success': True})
    # response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    return response
    # return jsonify({'success': True})

@app.route('/api/login', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user = users.find_one({'email': email})
    print(user)
    if user:
        name = user['name']
        email = user['email']
        role = user['role']
        user_object = {
            'name': name,
            'email': email,
            'role': role
        }
    else:
        return jsonify({'message': 'User does not exist', 'success': False})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials', 'success': False})
    access_token = create_access_token(identity=email)
    response = jsonify({'access_token': access_token, 'user': user_object, 'success': True})
    # response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    return response
    # return jsonify({'access_token': access_token, 'user': user_object, 'success': True})

@app.route('/api/postjobs', methods=['POST'])
@jwt_required()
@cross_origin()
def post_job():
    
    data = request.get_json()
    current_user = users.find_one({'email': data['email']})
    if current_user['role'] != 'employer':
        return jsonify({'message': 'Unauthorized access', 'success': False})
    title = data['title']
    description = data['description']
    location = data['location']
    mobile = data['phone']
    job = Job(title, description, location, mobile)
    jobs.insert_one(job.__dict__)
    return jsonify({'message': 'Job posted successfully', 'success': True})
@app.route('/api/jobs', methods=['GET'])
@cross_origin()
@jwt_required()
def get_jobs():
    alljobs = jobs.find({}, {'_id': 0, 'title': 1, 'description': 1, 'location': 1, 'mobile': 1} )
    print(alljobs)
    job_list = []
    for job in alljobs:
        job_dict = {
            'title': job['title'],
            'description': job['description'],
            'location': job['location'],
            'mobile': job['mobile']
        }
        job_list.append(job_dict)
        print(job_list)
    return jsonify({'jobs': job_list, 'success': True})
    # return jsonify({'message': 'Jobs fetched successfully'})
if __name__ == '__main__':
    app.run(debug=True)
