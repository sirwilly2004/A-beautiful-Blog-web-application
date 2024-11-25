import bleach
from flask import render_template, redirect, url_for, request,flash,abort,jsonify
from flaskblog import app,db
from flask_login import login_user, login_required, logout_user,current_user
from flaskblog import bcrypt
from flaskblog.models import Post, User,Category,Subscriber,Comment
from datetime import datetime
from .utils import notify_users_about_post,save_picture,send_reset_email,allowed_file


@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    
    user_comment = request.form.get('comment')
    if user_comment:
        if current_user.is_authenticated:
            # Sanitize the comment before saving
            allowed_tags = ['b', 'i', 'u', 'p', 'strong', 'em', 'a']
            allowed_attrs = {'a': ['href', 'title']}
            sanitized_comment = bleach.clean(user_comment, tags=allowed_tags, attributes=allowed_attrs)
            
            comment = Comment(user_id=current_user.id, post_id=post_id, content=sanitized_comment)
            db.session.add(comment)
            db.session.commit()
            flash("Comment added successfully.", "success")
        else:
            flash('You need to be logged in to comment.', 'warning')
            return redirect(url_for('login'))
    
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
    return render_template('post-and-comments.html', post=post, comments=comments)

@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('search')
    results = []
    
    if search_query:
        # Use the filter to search posts with case-insensitive matching on the title
        results = Post.query.filter(Post.title.ilike(f'%{search_query}%')).all()
    
    # Render search results to a template, or you could redirect back to the home page with the search results
    return render_template('search-results.html', results=results, query=search_query)
 

@app.route('/', methods=['GET'])
def home_page():
    categories = Category.query.all()  # Retrieve all categories
    # Query Parameters
    page = request.args.get('page', 1, type=int)  
    per_page = 6
    total_posts = Post.query.count()  # Get the total number of posts in the model
    total_pages = (total_posts + per_page - 1) // per_page  # Calculate total pages in the model

    # Fetch the posts for the current page, ordered by date_posted descending
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page, error_out=False).items  # Fetch posts for the current page
    # Calculate previous and next page numbers
    previous_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    return render_template('index.html', posts=posts, 
                           current_page=page, 
                           total_pages=total_pages, 
                           previous_page=previous_page, 
                           next_page=next_page, 
                           categories=categories)

@app.route('/about')
def about():
    category = Category.query.all()
    return render_template('about.html', title='About', category=category)




@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))  # Redirect if already logged in

    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if not user:
            flash('This email does not exist', 'danger')
            return redirect(url_for('login'))
        if not bcrypt.check_password_hash(user.password, request.form['password']):
            flash('Incorrect password, try again', 'danger')
            return redirect(url_for('login'))
        
        remember = 'remember' in request.form  # Check if 'remember me' is selected
        login_user(user, remember=remember)
        flash(f'{current_user.username} you have been logged in enjoy your stay on the site ')
        # Handle the redirection to the original page after login
        next_page = request.args.get('next')  # Retrieve the 'next' parameter
        return redirect(next_page) if next_page else redirect(url_for('home_page'))
    return render_template('login.html', title='Login')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists. Please log in instead.', 'warning')
            return redirect(url_for('login'))
        
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        username = request.form.get('name')

        if password == confirm_password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(email=email, password=hashed_password, username=username)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match. Please check your password.', 'danger')
    
    return render_template('register.html', title='register')

@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    next_page = request.args.get('next')  # Check for 'next' in the query string

    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form['title']
        category_id = request.form['category_id']
        description = request.form['description']
        content = request.form['content'] 
        image_url = request.form.get('image_url')
        if image_url:
        # Validate the image URL here if necessary
            if not image_url.startswith("http"):
                flash('Invalid image URL format', 'danger')
                return redirect(url_for('create_post'))

        # create a new instance of the post class
        new_post = Post( title=title, description=description,  
                        content=content,
                        user_id=current_user.id,
                        image_url=image_url,
                        date_posted=datetime.utcnow(),
                        category_id= category_id)
        try:
            db.session.add(new_post)
            db.session.commit()
            flash('Post created successfully!', 'success')

            # Notify all the subscribers or users about the new post and send it to there gmail
            notify_users_about_post(new_post)
            print('sent the message to the user of the post')
            return redirect(next_page or url_for('home_page')) # Redirect to a view after success
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash('Error creating post: {}'.format(str(e)), 'danger')
        # fetch all the product category database
    return render_template('create-post.html', title='create post', categories=categories)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    subscribers = Subscriber.query.all()
    email = request.form.get('email')
    subscribers = Subscriber.query.filter_by(email=email).first()
    if subscribers:
        flash('You have use this email to subscribe before','danger')
        return redirect(url_for('home_page'))
    new_subscriber = Subscriber(email=email)
    db.session.add(new_subscriber)
    db.session.commit()
    flash('Thank you for subscribing to our newsletter!', 'success')

    return redirect(url_for('home_page'))

@app.route('/delete-post/<int:post_id>',methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    for comment in post.comments:
        db.session.delete(comment)
        
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('home_page'))

@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    categories = Category.query.all()
    post = Post.query.get_or_404(post_id)
    # This Ensure only the author can edit the post
    if post.author != current_user:
        abort(403)
    # check if the request is equal to post 
    if request.method == 'POST':
        # Print to verify if form data is being sent
        # print(request.form)

        # Get form data with a fallback to an empty string
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id', '').strip()
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '').strip()
        image_url = request.form.get('image_url', '').strip()


        # Check if all fields have data before committing them to the database 
        if title and category_id and description and content:
            post.title = title
            post.category_id = category_id
            post.description = description
            post.content = content
            post.image_url = image_url
            db.session.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('home_page'))
        else:
            flash('All fields are required.', 'danger')

    return render_template('create-post.html', title='Edit Post', post=post, categories=categories)


# forgot password reset code is here 
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            if send_reset_email(user):
                flash('An email has been sent with instructions to reset your password.', 'info')
            else:
                flash('An error occurred. Please try again later.', 'danger')
        else:
            flash('Email address not found.', 'danger')
        return redirect(url_for('forgot_password'))
    return render_template('forgot-password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password == confirm_password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated! You are now able to log in', 'success')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match.', 'danger')
    return render_template('reset_password.html', token=token)

# copied from vo


@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        email = request.form.get('email')
        location = request.form.get('location')
        website = request.form.get('website')
        short_bio = request.form.get('short_bio')
        long_bio = request.form.get('long_bio')

        # Update user attributes
        current_user.username = username
        current_user.email = email
        current_user.location = location
        current_user.website = website
        current_user.short_bio = short_bio
        current_user.long_bio = long_bio

        # Handle profile picture upload
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar and allowed_file(avatar.filename):
                try:
                    picture_filename = save_picture(avatar)
                    current_user.image_file = picture_filename
                except Exception as e:
                    return jsonify({"success": False, "message": f"Error saving image: {str(e)}"})

        try:
            # Commit changes to the database
            db.session.commit()
            return jsonify({"success": True, "message": "Profile updated successfully!"})
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            return jsonify({"success": False, "message": f"Error updating profile: {str(e)}"})

    return jsonify({"success": False, "message": "Invalid request method"})

@app.route('/profile')
@login_required
def user_profile():
    image_file = url_for('static', filename='users/profile-pics/' + current_user.image_file)
    return render_template('user_profile.html', title='Profile', user=current_user, image_file=image_file)


# code for the redirecting user when they try to go to a page that required the user to be login and it get them back to the place they try to access
#  next_page = request.args.get('next')
# return redirect(next_page) if next_page else redirect(url_for('home_page'))
