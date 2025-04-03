import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_mail import Mail, Message
from sqlalchemy import LargeBinary
from celery import Celery
from flask_migrate import Migrate
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Aid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aid_type = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Login Manager Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Role-Based Access Decorator
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if current_user.role != role:
                flash('Access denied', 'danger')
                return redirect(url_for('index'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# Routes
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome {user.role}', 'success')
            return redirect(url_for(user.role.lower()))
        flash('Invalid credentials', 'danger')
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['email']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['password1']
        role = request.form['role']
        
        if password != confirm_password:
            flash("Passwords do not match!", 'danger')
            return render_template('register.html')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!", 'danger')
            return render_template('register.html')
        
        new_user = User(username=username, email=email, password=generate_password_hash(password), role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", 'success')
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
@role_required('Admin')
def admin():
    return render_template("admin.html")

@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/student')
@login_required
@role_required('Student')
def student():
    return render_template("student.html")

@app.route('/donor')
@login_required
@role_required('Donor')
def donor():
    return render_template("donor.html")

@app.route('/bursaries')
def bursary_view():
    page = request.args.get('page', 1, type=int)
    bursaries = Aid.query.filter_by(aid_type='Bursary').paginate(page=page, per_page=10)
    return render_template('bursary_view.html', bursaries=bursaries)



if __name__ == '__main__':
    app.run(debug=True)
