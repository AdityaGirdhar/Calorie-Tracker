from flask import Flask, redirect, url_for, flash, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import Config
from models import db, User, Entry
from requests import request

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes and other application logic go here
@app.route('/')
def home():
    return "Welcome to Dive's Calorie Tracker API."

# Example login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Retrieve the user from the database based on the username
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # If the user exists and the password is correct, log in the user
        login_user(user)
        # Rest of the login logic
        return redirect(url_for('dashboard'))
    else:
        # Invalid credentials, handle authentication failure
        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))
    # Validate user credentials
    # ...
    # Assuming user is the authenticated user object
    user
    login_user(user)
    # Rest of the login logic
    
# Example protected route
@app.route('/dashboard')
@login_required
def dashboard():
    # Route logic for authenticated users
    # ...
    pass

@app.route('/profile')
@login_required
def profile():
    user = current_user
    # Rest of the route logic
    
# Example protected route with role-based authorization
@app.route('/admin')
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
        # Handle unauthorized access
        pass
    # Rest of the route logic for admin users


"""
# ERROR HANDLING #

Errors are returned as JSON and are formatted in the following manner:

	{
		"success": False,
		"error": error_code,
		"message": descriptive_reason
	}

"""
@app.errorhandler(404)
def not_found(error):
	return jsonify({
		'success': False,
		'error': 404,
		'message': 'Resource not found'
	}), 404

@app.errorhandler(500)
def server_error(error):
	return jsonify({
		'success': False,
		'error': 500,
		'message': 'Internal server error'
	}), 500

@app.errorhandler(422)
def unprocessable(error):
	return jsonify({
		'success': False,
		'error': 422,
		'message': 'Unprocessable'
	}), 422

@app.errorhandler(400)
def bad_request(error):
	return jsonify({
		'success': False,
		'error': 400,
		'message': 'Bad request',
	}), 400
 
@app.errorhandler(403)
def forbidden(error):
	return jsonify({
		'success': False,
		'error': 403,
		'message': 'Resource forbidden',
	}), 403

if __name__ == '__main__':
    app.run(debug=True)