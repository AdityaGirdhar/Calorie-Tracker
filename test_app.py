import unittest
from app import app, db
from models import User
from config import Config

import os
from dotenv import load_dotenv
load_dotenv()

class AppTestCase(unittest.TestCase):
	def setUp(self):
		self.app = app.test_client()
		self.app_context = app.app_context()
		self.app_context.push()
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
		db.create_all()
		if not User.query.filter_by(username='admin').first():
			new_user = User(username='admin', expected_calories=2000, role='admin')
			new_user.set_password('admin')
			db.session.add(new_user)
			db.session.commit()

	def tearDown(self):
		self.app_context.pop()

	# Testing connection and GET /
	def test_home_page(self):
		response = self.app.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data, b"Welcome to Calorie Tracker API.")


	# Testing POST /login (valid credentials)
	def test_login_success(self):
		# Preparing correct login credentials and sending request
		request_data = {
			'username': 'admin',
			'password': 'admin'
		}
		# Get the response data and extracting JSON
		response = self.app.post('/login', json=request_data)
		response_data = response.get_json()
		# Assert the response status code
		self.assertEqual(response.status_code, 200)
		# Assert the response data against the expected data
		self.assertTrue(response_data['success'])
		response = self.app.post('/logout')

	# Testing POST /login (invalid credentials)
	def test_login_failure(self):
		# Preparing invalid login credentials and sending request
		request_data = {
			'username': 'no_user',
			'password': 'no_password'
		}
		# Get the response data and extracting JSON
		response = self.app.post('/login', json=request_data)
		response_data = response.get_json()
		# Assert the response status code
		self.assertEqual(response.status_code, 200)
		# Assert the response data against the expected data
		self.assertFalse(response_data['success'])
  
	# Testing POST /session and POST /logout
	def test_session_and_logout(self):
		# Preparing valid login credentials and sending request
		request_data = {
			'username': 'admin',
			'password': 'admin'
		}
		self.app.post('/login', json=request_data)
		response = self.app.post('/session')
		response_data = response.get_json()
  
		# Assert the response status code
		self.assertEqual(response.status_code, 200)
		# Assert the response data against the expected data
		self.assertTrue(response_data['success'])
  
		response = self.app.post('/logout')
		response_data = response.get_json()
		# Assert the response status code
		self.assertEqual(response.status_code, 200)
		# Assert the response data against the expected data
		self.assertTrue(response_data['success'])
  
	# Testing POST /signup (new user)
	def test_signup_and_deletion(self):
		# Preparing valid login credentials and sending request
		response = self.app.post('/signup', json={
			'username': 'new_user',
			'password': 'new_user',
			'expected_calories': 2000
		})
		response_data = response.get_json()
		# Assert the response status code
		self.assertEqual(response.status_code, 200)
		# Assert the response data against the expected data
		self.assertTrue(response_data['success'])
  
		response = self.app.post('/login', json={
			'username': 'new_user',
			'password': 'new_user'
		})
		response_data = response.get_json()
  
		# Assert the response status code
		self.assertEqual(response.status_code, 200)
		# Assert the response data against the expected data
		self.assertTrue(response_data['success'])
  
		response = self.app.delete('/users', json={ 'username': 'new_user' })
		response_data = response.get_json()
		# Assert the response status code
		self.assertEqual(response.status_code, 200)
		# Assert the response data against the expected data
		self.assertTrue(response_data['success'])

 
	# Testing POST /signup (existing user)
	def test_invalid_signup(self):
		# Preparing invalid signup credentials and sending request
		response = self.app.post('/signup', json={
			'username': 'admin',
			'password': 'admin',
			'expected_calories': 2000
		})
		response_data = response.get_json()
		# Assert the response status code
		self.assertEqual(response.status_code, 200)
		# Assert the response data against the expected data
		self.assertFalse(response_data['success'])

	# Testing GET /users (role-based access)
	def test_user_pagination(self):
		response = self.app.post('/signup', json={
			'username': 'user',
			'password': 'user',
			'expected_calories': 2000
		})
		self.assertTrue(response.get_json()['success'])
		response = self.app.post('/login', json={ 'username': 'user', 'password': 'user' })
		self.assertTrue(response.get_json()['success'])
		response = self.app.get('/users')
		self.assertFalse(response.get_json()['success'])
		response = self.app.delete('/users', json={ 'username': 'user' })
		self.assertTrue(response.get_json()['success'])
		response = self.app.post('/login', json={ 'username': 'admin', 'password': 'admin' })
		self.assertTrue(response.get_json()['success'])
		response = self.app.get('/users', json={ 'limit': 1 })
		self.assertTrue(response.get_json()['success'])
		self.assertTrue(response.get_json()['limit'] == 1)

	# Testing POST /records (role-based access, Nutritionix API)
	def test_api(self):
		response = self.app.post('/login', json={ 'username': 'admin', 'password': 'admin' })
		self.assertTrue(response.get_json()['success'])
		response = self.app.post('/records', json={ 'text': 'banana' })
		self.assertTrue(response.get_json()['success'])

if __name__ == '__main__':
	unittest.main(verbosity=2)