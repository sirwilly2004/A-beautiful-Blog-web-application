from flask_login import UserMixin
from flaskblog import db, login_manager
from datetime import datetime
from flask import current_app
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer as Serializer



user_interest = db.Table('user_interest',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'), primary_key=True)
)

class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # Use a foreign key to reference the category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)    
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_url = db.Column(db.String(500), nullable=True) 
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comments = db.relationship('Comment', back_populates='post')
    

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    # additional property added to the user model to make use of in the profile page
    short_bio = db.Column(db.String(150), nullable=True)  # For brief descriptions
    long_bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)  # User's location
    website = db.Column(db.String(120), nullable=True)  # User's website URL
    joined_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 

    interests = db.relationship('Interest', secondary=user_interest, backref=db.backref('users', lazy='dynamic')) 

    posts = db.relationship('Post', backref='author', lazy=True)

    comments = db.relationship('Comment', back_populates='user')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        # Generate token with expiration time by adding an expiration field in the payload
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, max_age=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # Load the token and set max_age to define the token’s expiration period
            user_id = s.loads(token, max_age=max_age)['user_id']
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
        return User.query.get(user_id)
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    posts = db.relationship('Post', backref='category', lazy=True)


    def __repr__(self):
        return f"<Category {self.name}>"
    
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"Subscriber('{self.email}')"

def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.joined_date}')"
        

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    user = db.relationship('User', back_populates='comments')
    post = db.relationship('Post', back_populates='comments')
