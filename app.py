from flask import Flask, redirect, url_for, flash, abort, jsonify, render_template, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Entry
from config import Config
from nutritionix import get_calories
from datetime import datetime, date, time

import os
from dotenv import load_dotenv
load_dotenv()

def get_paginated_filtered_records(user_id, date=None, text=None, calories_min=None, calories_max=None, page=None, limit=None):
	base_query = Entry.query.filter_by(user_id=user_id)
	if date:
		base_query = base_query.filter(Entry.date == date)
	if text:
		base_query = base_query.filter(Entry.text.ilike(f"%{text}%"))
	if calories_min:
		base_query = base_query.filter(Entry.calories >= calories_min)
	if calories_max:
		base_query = base_query.filter(Entry.calories <= calories_max)

	# Calculate the offset and limit for pagination
	offset = ((page - 1) * limit) if (page != None and limit != None) else None
	# Apply pagination to the query
	records_query = base_query.offset(offset).limit(limit)
	# Retrieve the records from the database
	records = records_query.all()
	# Get the total count of records for pagination
	total_count = base_query.count()
 
	return records, total_count

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db.init_app(app)

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# Routes and other application logic go here
@app.route('/')
def home():
	return "Welcome to Calorie Tracker API."

# Example login route
@app.route('/login', methods=['POST'])
def login():
	data = request.get_json()
	try:
		username = data['username']
		password = data['password']
	except:
		abort(400)

	# Retrieve the user from the database based on the username
	user = User.query.filter_by(username=username).first()
 
	if user and user.check_password(password):
		# If the user exists and the password is correct, log in the user
		login_user(user)
		# Rest of the login logic
		return jsonify({
			'success' : True,
			'username' : username,
			'message' : "Logged in successfully"
		})
	else:
		# Invalid credentials, handle authentication failure
		return jsonify({
			'success': False,
			'error': 400,
			'message': f'User {username} does not exist'
		})
	
@app.route('/signup', methods=['POST'])
def signup():
	if request.method == 'POST':
		data = request.get_json()
		try:
			username = data['username']
			password = data['password']
			expected_calories = int(data['expected_calories'])
		except:
			abort(400)

		# Check if the username is already taken
		existing_user = User.query.filter_by(username=username).first()
		if existing_user:
			return jsonify({
				'success': False,
				'error': 422,
				'message': f'User {username} already exists'
			})
  
		# Create a new user object
		new_user = User(username=username, expected_calories=expected_calories, role='user')
		new_user.set_password(password)

		# Add the new user to the database
		db.session.add(new_user)
		db.session.commit()

		return jsonify({
			'success' : True,
			'username' : username,
			'message' : "User created successfully"
		})

@app.route('/users', methods=['GET'])
@login_required
def get_users():
	try:
		data = request.get_json()
	except:
		data = {}
  
	# Get the query parameters for filtering
	username = data['username'] if 'username' in data else None
	user_id = data['user_id'] if 'user_id' in data else None
	print(user_id)
	role = data['role'] if 'role' in data else None
	base_query = User.query

	if user_id:
		base_query = base_query.filter(User.id == user_id)
	if username:
		base_query = base_query.filter(User.username == username)
	if role:
		base_query = base_query.filter(User.role == role)
  
	try:
		page = int(data['page']) if 'page' in data else None
		limit = int(data['limit']) if 'limit' in data else None
	except:
		abort(400)

	# Calculate the offset and limit for pagination
	offset = ((page - 1) * limit) if (page != None and limit != None) else None
	# Apply pagination to the query
	records_query = base_query.offset(offset).limit(limit)
	# Retrieve the records from the database
	records = records_query.all()
	# Get the total count of records for pagination
	total_count = base_query.count()
 
	if role:
		if (current_user.role not in { 'manager', 'admin' }):
			abort(403)
		res = { 'users' : [], 'managers' : [], 'admins' : [] }
		for user in records:
			res[user.role + 's'].append({ 'user_id': user.id, 'username': user.username, 'expected_calories': user.expected_calories})
		return jsonify({ 'users': res, 'total_count': total_count, 'page': page, 'limit': limit })

	# Only allow access if user's role is manager or admin
	if (current_user.role == 'manager' or current_user.role == 'admin'):
		res = { 'users' : [], 'managers' : [], 'admins' : [] }
		for user in records:
			res[user.role + 's'].append({ 'user_id': user.id, 'username': user.username, 'expected_calories': user.expected_calories})
		return jsonify({ 'users': res, 'total_count': total_count, 'page': page, 'limit': limit })
	else:
		abort(403)
  
@app.route('/users', methods=['PUT'])
@login_required
def post_users():
	if (current_user.role == 'user'):
		data = request.get_json()
		try:
			expected_calories = data['expected_calories']
		except:
			abort(400)
		user = User.query.filter_by(username=current_user.username).first()
		user.expected_calories = expected_calories
		db.session.commit()
		return jsonify({
			'success': True,
			'message': 'Expected calories updated'
		})

	# Only allow access to change role if user's role is manager or admin
	if (current_user.role == 'manager' or current_user.role == 'admin'):
		data = request.get_json()
		try:
			username = data['username']
			role = data['role']
		except:
			abort(400)

		# Retrieve the user from the database based on the username
		user = User.query.filter_by(username=username).first()
		if current_user.username == username:
			abort(403)
		if current_user.role == 'manager' and role == 'admin':
			abort(403)

		if user:
			# Update the user's role with the new value
			previous_role = user.role
			user.role = role
			db.session.commit()
			return jsonify({
				'success': True,
				'username': username,
				'previous_role': previous_role,
				'new_role': role,
				'message': f'Role successfully updated'
			})
		else:
			return jsonify({
				'success': False,
				'error': 400,
				'message': f'User {username} does not exist'
			})

@app.route('/users', methods=['DELETE'])
@login_required
def delete_users():
	data = request.get_json()
	try:
		username = data['username']
	except:
		abort(400)
	if current_user.username == username:
		return jsonify({
			'success': False,
			'error': 422,
			'message': 'Can not delete self'
		})

	if (current_user.role in {'manager', 'admin'}):
		user = User.query.filter_by(username=username).first()
		if user:
			if (current_user.role == 'manager' and user.role in {'manager', 'admin'}):
				abort(403)
			db.session.delete(user)
			db.session.commit()
			return jsonify({
				'success': True,
				'username': user.username,
				'message': f'User {user.username} successfully deleted'
			})
		else: return jsonify({
			'success': False,
			'error': 400,
			'message': f'User {username} does not exist'
		})
	else:
		abort(403)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
	username = current_user.username
	logout_user()
	return jsonify({
		'success' : True,
		'username' : username,
		'message' : "Logged out successfully"
	})

@app.route('/session', methods=['POST'])
@login_required
def session():
	user = current_user
	return jsonify({
		'username': user.username,
		'role': user.role
	})
	
@app.route('/records', methods=['GET'])
@login_required
def get_records():
	data = request.get_json()
	# Get the query parameters for filtering
	date = data['date'] if 'date' in data else None
	text = data['text'] if 'text' in data else None
	calories_min = data['calories_min'] if 'calories_min' in data else None
	calories_max = data['calories_max'] if 'calories_max' in data else None

	try:
		python_date = datetime.strptime(date, '%Y-%m-%d').date() if date else None
	except:
		abort(400)
    
	# Get the pagination parameters
	try:
		page = int(data['page']) if 'page' in data else None
		limit = int(data['limit']) if 'limit' in data else None
	except:
		abort(400)

	if current_user.role == 'user':
		# For users with the 'user' role, retrieve their own records
		user_id = current_user.id
  
		records, total_count = get_paginated_filtered_records(user_id, date, text, calories_min, calories_max, page, limit)

		records_formatted = [{
			'id': entry.id,
			'text': entry.text,
			'date': str(entry.date),
			'time': str(entry.time),
			'calories': entry.calories,
			'is_below_expected': entry.is_below_expected
		} for entry in records]

		return jsonify({
			'records': records_formatted,
			'total_count': total_count,
			'page': page,
			'limit': limit
		})

	elif current_user.role == 'admin':
		user_id = data['user_id'] if 'user_id' in data else None
		id = data['id'] if 'id' in data else None

		if id:
			entry = Entry.query.filter_by(id=id).first()
			return jsonify({
				'records': ({
					'id': entry.id,
					'text': entry.text,
					'date': str(entry.date),
					'time': str(entry.time),
					'calories': entry.calories,
					'is_below_expected': entry.is_below_expected
				} if entry else {})
			})

		if user_id:
			records, total_count = get_paginated_filtered_records(user_id, date, text, calories_min, calories_max, page, limit)

			records_formatted = [{
				'id': entry.id,
				'text': entry.text,
				'date': str(entry.date),
				'time': str(entry.time),
				'calories': entry.calories,
				'is_below_expected': entry.is_below_expected
			} for entry in records]

			return jsonify({
				'records': records_formatted,
				'total_count': total_count,
				'page': page,
				'limit': limit
			})
   
		# For users with the 'admin' role, retrieve records of all users
		users = User.query.all()
		user_records = {}
  
		for user in users:
			if (user.role == 'manager'):
				continue
   
			records, total_count = get_paginated_filtered_records(user.id, date, text, calories_min, calories_max, page, limit)
   
			records_formatted = [{
				'id': entry.id,
				'text': entry.text,
				'date': str(entry.date),
				'time': str(entry.time),
				'calories': entry.calories,
				'is_below_expected': entry.is_below_expected,
				'page': page,
				'total_count': total_count,
				'limit': limit
			} for entry in records]
			user_records[user.username] = records_formatted
   
		return jsonify({
			'records': user_records
		})
	else:
		# For unauthorized users, return a 403 Forbidden error
		return abort(403)
 
@app.route('/records', methods=['POST'])
@login_required
def post_records():
	user = current_user
	if user.role == 'user' or user.role == 'admin':
		data = request.get_json()
		user_id = user.id
		if user.role == 'admin':
			if 'user_id' in data:
				user_id = data['user_id']
		if 'text' not in data:
			abort(400)
		if 'calories' not in data:
			# If user does not provide calories, we fetch it from Nutrionix API
			food_name, calories = get_calories(data['text'])
			if food_name == None or calories == None:
				return jsonify({
					'success': False,
					'error': 422,
					'message': 'Calorie data not provided and food item does not exist on Nutritionix database'
				})
			else:
				data['calories'] = calories
				data['text'] = food_name
		calories_sum = 0
		# This piece of code can be optimised by modifying database design and including a calories_sum that resets to 0 each day, preventing recomputation on each POST
		for record in Entry.query.filter_by(date=datetime.now().date()).all():
			calories_sum += record.calories
		calories_sum += int(data['calories'])
		expected_calories = User.query.filter_by(id=user_id).first().expected_calories
		entry = Entry (
			user_id = user_id,
			date = datetime.now().date(),
			time = datetime.now().time(),
			text = data['text'],
			calories = data['calories'],
			is_below_expected = (calories_sum < expected_calories)
		)
		db.session.add(entry)
		db.session.commit()
		return jsonify({
			'success': True,
			'message': 'Added record'
		})
	else:
		abort(403)

@app.route('/records', methods=['DELETE'])
@login_required
def delete_records():
	user = current_user
	if user.role == 'user' or user.role == 'admin':
		data = request.get_json()
		if 'id' not in data:
			abort(400)
		record = Entry.query.filter_by(id=data['id']).first()
		if not record:
			return jsonify({
				'success': False,
				'error': 400,
				'message': 'Record does not exist'
			})
		if user.role == 'user' and user.id != record.user_id:
			abort(403)
		db.session.delete(record)
		db.session.commit()
		return jsonify({
			'success': True,
			'message': 'Successfully removed'
		})
	else:
		abort(403)
    
@app.route('/records', methods=['PUT'])
@login_required
def put_records():
	user = current_user
	if user.role == 'user' or user.role == 'admin':
		data = request.get_json()
		if 'id' not in data:
			abort(400)
		record = Entry.query.filter_by(id=data['id']).first()
		if not record:
			return jsonify({
				'success': False,
				'error': 400,
				'message': 'Record does not exist'
			})
		if user.role == 'user' and user.id != record.user_id:
			abort(403)
		if 'calories' in data:
			record.calories = data['calories']
		if 'text' in data:
			record.text = data['text']
		db.session.commit()
		return jsonify({
			'success': True,
			'message': 'Successfully modified'
		})

"""
# ERROR HANDLING #

Errors are returned as JSON and are formatted in the following manner:

	{
		"success": False,
		"error": error_code,
		"message": descriptive_reason
	}

"""

@app.errorhandler(400)
def bad_request(error):
	return jsonify({
		'success': False,
		'error': 400,
		'message': 'Bad request',
	}), 400
 
@app.errorhandler(401)
def unauthorised(error):
	return jsonify({
		'success': False,
		'error': 401,
		'message': 'Unauthorised',
	}), 401
 
@app.errorhandler(403)
def forbidden(error):
	return jsonify({
		'success': False,
		'error': 403,
		'message': 'Forbidden request',
	}), 403

@app.errorhandler(404)
def not_found(error):
	return jsonify({
		'success': False,
		'error': 404,
		'message': 'Resource not found'
	}), 404
 
@app.errorhandler(405)
def invalid_method(error):
	return jsonify({
		'success': False,
		'error': 405,
		'message': 'Method not allowed'
	}), 405

@app.errorhandler(422)
def unprocessable(error):
	return jsonify({
		'success': False,
		'error': 422,
		'message': 'Unprocessable'
	}), 422
 
@app.errorhandler(500)
def server_error(error):
	return jsonify({
		'success': False,
		'error': 500,
		'message': 'Internal server error'
	}), 500
 
if __name__ == '__main__':
	with app.app_context():
		db.create_all()
		if not User.query.filter_by(username='admin').first():
			new_user = User(username='admin', expected_calories=2000, role='admin')
			new_user.set_password('admin')
			db.session.add(new_user)
			db.session.commit()
   
	app.run(debug=True)