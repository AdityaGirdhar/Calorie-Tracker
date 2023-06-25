from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)
	role = db.Column(db.String(64), nullable=False)
	expected_calories = db.Column(db.Integer, nullable=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	def __repr__(self):
		return '<User {}>'.format(self.username)

class Entry(db.Model):
	def __init__(self, *args, **kwargs):
		super(Entry, self).__init__(*args, **kwargs)
		self.calculate_is_below_expected()
	
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	date = db.Column(db.Date, nullable=False)
	time = db.Column(db.Time, nullable=False)
	text = db.Column(db.String(256), nullable=False)
	calories = db.Column(db.Integer, nullable=False)
	is_below_expected = db.Column(db.Boolean)

	user = db.relationship('User', backref=db.backref('entries', lazy=True))
	
	def calculate_is_below_expected(self):
		user = User.query.get(self.user_id) if self.user_id is not None else None
		
		if user is not None:
			total_calories = Entry.query \
				.filter(Entry.user_id == self.user_id, Entry.date == self.date) \
				.with_entities(db.func.sum(Entry.calories)).scalar()
			if total_calories is None:
				total_calories = 0
			# Add the calories of the current entry
			total_calories += self.calories
			# Compute whether total_calories is below the expected value
			self.is_below_expected = total_calories < user.expected_calories
		else:
			self.is_below_expected = False