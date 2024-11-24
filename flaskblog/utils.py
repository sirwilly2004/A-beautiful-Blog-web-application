from .models import Subscriber
from flask_login import current_user
from flask_mail import Message,Mail
from flask import url_for
import os
import secrets
from PIL import Image
from flaskblog import app

mail = Mail(app)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/users/profile-pics', picture_filename)
    
    # Resize the image
    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)
    
    return picture_filename


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  recipients=[user.email], sender='Techblog.com')
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}

If you did not make this request, simply ignore this email and no changes will be made.
'''
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False



def notify_users_about_post(post):
    users = Subscriber.query.filter(Subscriber.id != current_user.id).all()  # Exclude the current user
    for user in users:
        # Generate a short snippet of the post content (e.g., first 200 characters)
        snippet = post.content[:200] + '...' if len(post.content) > 200 else post.content

        # add a decorator here 
        decorated_snippet = f"""
        ------------------------------
        {snippet}
        ------------------------------
        """
        
        msg = Message(
            subject=f"New Post Notification: {post.title}",
            recipients=[user.email]
        )
        
        # Plain text version
        plain_text_body = f"""
        Hi {user.email},
        A new post titled *"{post.title}"* has just been published by {current_user.username} on Code Myhobby. Here's a short snippet:
        
        {decorated_snippet}

        Click here to read the full post: {url_for('post_detail', post_id=post.id, _external=True)}

        Regards,
        The Blog Team
        """

        # Attach the plain text content to the email
        msg.body = plain_text_body

        try:
            mail.send(msg)
            print(f"Email sent to {user.email}")
        except Exception as e:
            print(f"Failed to send email to {user.email}: {e}")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}
