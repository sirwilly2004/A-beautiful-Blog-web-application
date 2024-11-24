from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_mail import Mail


app =  Flask(__name__)
app.config['SECRET_KEY'] = '225635GDUEAHSGDY7333'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Blog.db'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'static/users/profile-pics'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)



MAIL_SERVER = app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
MAIL_PORT = app.config['MAIL_PORT'] = 587
MAIL_USERNAME = app.config['MAIL_USERNAME'] = 'williamsolaolu5@gmail.com'  # Use your actual Gmail address
MAIL_PASSWORD = app.config['MAIL_PASSWORD'] = 'kgggg'     # Use your generated App Password
MAIL_USE_TLS = app.config['MAIL_USE_TLS'] = True
MAIL_USE_SSL = app.config['MAIL_USE_SSL'] = False
MAIL_DEFAULT_SENDER = app.config['MAIL_DEFAULT_SENDER'] = ('Code myhobby', 'williamsolaolu5@gmail.com')

mail = Mail(app)
# ''(use later second password)
# 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    from flaskblog.models import User
    return User.query.get(int(user_id))


from flaskblog import routes

