from flask import Flask
from config import Config
from models import db, User, Entry

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Import the models after initializing the db instance
from models import User, Entry

# Routes and other application logic go here
@app.route('/')
def hello_world():
    return 'Hello, world!'

if __name__ == '__main__':
    app.run(debug=True)