import unittest
from datetime import datetime, date, time
from models import User, Entry
from app import app, db

class UserModelTestCase(unittest.TestCase):
	def test_password_hashing(self):
		# Create a User instance
		user = User(
			username='test',
			role='test',
			expected_calories=2000
			)
		password = 'sample_password'
		
		# Call the set_password method
		user.set_password(password)
		
		# Assert the expected outcomes
		self.assertTrue(user.check_password(password))
		self.assertFalse(user.check_password('some_other_password'))
	
class TestBackReference(unittest.TestCase):
	def setUp(self):
    	# Step 1: Initialize a database instance
		self.app = app.test_client()
		self.app_context = app.app_context()
		self.app_context.push()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_back_reference(self):
		# Step 2: Add a dummy user
		user = User(username='test_user', role='user', expected_calories=2000)
		user.set_password('sample_password')
		# Step 3: Add a dummy entry
		entry = Entry(user=user, date=datetime.now().date(), time=datetime.now().time(),
					  text='Test entry', calories=100, is_below_expected=False)

		with self.app_context:
			# Add the user and entry to the session
			db.session.add(user)
			db.session.add(entry)
			db.session.commit()

			# Query the user from the database
			user = User.query.filter_by(username='test_user').first()

			# Check the back reference
			self.assertIn(entry, user.entries)
   
class TestCalculateIsBelowExpected(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_calculate_is_below_expected(self):
        # Create a new user with an expected calorie value
        user = User(username='test_user', role='user', expected_calories=2000)
        user.set_password('sample_password')
        db.session.add(user)
        
        user = User.query.filter_by(username='test_user').first()

        # Create multiple entries for different dates with different calorie values
        for i in range(3):
            entry = Entry(user_id=user.id, date=date(2023, 6, 18), time=time(12, 0), text=f'Entry {i}', calories=1000*i)
            db.session.add(entry)
        
        entries = Entry.query.all()

        # Iterate over the entries and assert the value of is_below_expected
        for entry in entries:
            self.assertEqual(entry.is_below_expected, entry.calories < user.expected_calories)

if __name__ == '__main__':
	unittest.main()