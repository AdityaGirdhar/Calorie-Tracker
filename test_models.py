import unittest
from datetime import datetime
from models import User, Entry
from app import db

class UserModelTestCase(unittest.TestCase):
    def test_password_hashing(self):
        # Create a User instance
        user = User(
            username='test',
            role='test'
        	)
        password = 'sample_password'
        
        # Call the set_password method
        user.set_password(password)
        
        # Assert the expected outcomes
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password('some_other_password'))
    
class EntryModelTestCase(unittest.TestCase):
    def test_db_relationship(self):
        # Create an Entry instance
        entry = Entry(
            text='sample_food',
            user_id=1,
            date=datetime.date(),
            time=datetime.time()
            calories=1500,
            )
        

if __name__ == '__main__':
	unittest.main()