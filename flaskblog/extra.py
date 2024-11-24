from flask import render_template, redirect, url_for, request,flash,abort,jsonify
from flaskblog import app,db,mail
from flask_login import login_user, login_required, logout_user,current_user
from flaskblog import bcrypt
from flaskblog.models import Post, User,Category,Subscriber,Comment
from datetime import datetime
from werkzeug.utils import secure_filename
from flaskblog.form import ResetPasswordForm,RequestResetForm
from flask_mail import Message
from .utils import notify_users_about_post,save_picture



@app.route('/add-posts')
def add_posts():
    user = User.query.first()

    # Define categories that should already be in the database
    category_names = ["Tech", "Food", "News"]
    categories = {category.name: category for category in Category.query.all()}

    # Sample data
    sample_posts = [
        {"title": "Exploring AI in 2024", "description": "An in-depth look at the latest in artificial intelligence.", "content": "Content on AI advancements.", "category": "Tech"},
        {"title": "Top 10 Healthy Recipes", "description": "Delicious and nutritious recipes to try this year.", "content": "Content on healthy recipes.", "category": "Food"},
        {"title": "Climate Change Updates", "description": "The latest news on climate change and its effects globally.", "content": "Content on climate change.", "category": "News"},
        {"title": "New iPhone Features", "description": "Apple's latest phone features.", "content": "Details on iPhone updates.", "category": "Tech"},
        {"title": "The Future of Renewable Energy", "description": "How renewable energy is shaping our world.", "content": "Insights on renewable energy.", "category": "Tech"},
        {"title": "Vegan Desserts to Try", "description": "Easy and tasty vegan dessert recipes.", "content": "Vegan dessert ideas.", "category": "Food"},
        {"title": "Election Results and Analysis", "description": "Breaking down the latest election results.", "content": "Analysis on election outcomes.", "category": "News"},
        {"title": "How to Make Sushi at Home", "description": "A beginner's guide to making sushi.", "content": "Step-by-step sushi-making guide.", "category": "Food"},
        {"title": "Advancements in Robotics", "description": "How robots are becoming part of everyday life.", "content": "Robotics in daily life.", "category": "Tech"}
    ]

    # Create and save posts
    for post_data in sample_posts:
        post = Post(
            title=post_data["title"],
            description=post_data["description"],
            content=post_data["content"],
            date_posted=datetime.utcnow(),
            user_id=user.id,
            category_id=categories[post_data["category"]].id
        )
        db.session.add(post)

    # Commit all new posts to the database
    db.session.commit()
    print("Sample posts created successfully!")
    return {'message': 'posts data added successfully'}


@app.route('/add')
def add_category():
    categories = ['Tech', 'Food', 'News', 'Finance']

    for category_name in categories:
        category = Category(name=category_name)
        db.session.add(category)
    db.session.commit()
    return 'Added Category Successful'

@app.route('/insert-data')
def sample_data():
    user = User.query.first()

    # Define categories that should already be in the database
    category_names = ["Tech", "Food", "News"]
    categories = {category.name: category for category in Category.query.all()}

    # Sample data
    sample_posts = [
        {"title": "Exploring AI in 2024", "description": "An in-depth look at the latest in artificial intelligence.", "content": "Content on AI advancements.", "category": "Tech"},
        {"title": "Top 10 Healthy Recipes", "description": "Delicious and nutritious recipes to try this year.", "content": "Content on healthy recipes.", "category": "Food"},
        {"title": "Climate Change Updates", "description": "The latest news on climate change and its effects globally.", "content": "Content on climate change.", "category": "News"},
        {"title": "New iPhone Features", "description": "Apple's latest phone features.", "content": "Details on iPhone updates.", "category": "Tech"},
        {"title": "The Future of Renewable Energy", "description": "How renewable energy is shaping our world.", "content": "Insights on renewable energy.", "category": "Tech"},
        {"title": "Vegan Desserts to Try", "description": "Easy and tasty vegan dessert recipes.", "content": "Vegan dessert ideas.", "category": "Food"},
        {"title": "Election Results and Analysis", "description": "Breaking down the latest election results.", "content": "Analysis on election outcomes.", "category": "News"},
        {"title": "How to Make Sushi at Home", "description": "A beginner's guide to making sushi.", "content": "Step-by-step sushi-making guide.", "category": "Food"},
        {"title": "Advancements in Robotics", "description": "How robots are becoming part of everyday life.", "content": "Robotics in daily life.", "category": "Tech"}
    ]

    # Create and save posts
    for post_data in sample_posts:
        post = Post(
            title=post_data["title"],
            description=post_data["description"],
            content=post_data["content"],
            date_posted=datetime.utcnow(),
            user_id=user.id,
            category_id=categories[post_data["category"]].id
        )
        db.session.add(post)

    # Commit all new posts to the database
    db.session.commit()
    return "Sample posts created successfully!"

