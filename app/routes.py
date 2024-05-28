from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User, Aid, db

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
aid_bp = Blueprint('aid', __name__)

@main_bp.route('/')
def index():
    return render_template("index.html")

@main_bp.route('/about')
def about():
    return render_template("about.html")

@main_bp.route('/contact')
def contact():
    return render_template("contact.html")

@main_bp.route('/admin')
@login_required
def admin():
    return render_template("admin.html")

@aid_bp.route('/aid_bursary_list')
def aid_bursary_list():
    bursaries = Aid.query.filter_by(aid_type='Bursary').all()
    return render_template('aid_bursary_list.html', bursaries=bursaries)

@aid_bp.route('/aid_scholarship_list')
def aid_scholarship_list():
    scholar = Aid.query.filter_by(aid_type='Scholarship').all()
    return render_template("aid_scholarship_list.html", scholarship=scholar)

@aid_bp.route('/aid_grant_list')
def aid_grant_list():
    grant = Aid.query.filter_by(aid_type='Grant').all()
    return render_template("aid_grant_list.html", grant=grant)

@main_bp.route('/student')
@login_required
def student():
    return render_template('student.html')

@aid_bp.route('/bursaries', methods=["GET"])
def bursary_view():
    bursaries = Aid.query.filter_by(aid_type='Bursary').all()
    return render_template('bursary_view.html', bursaries=bursaries)

@aid_bp.route('/scholarships', methods=["GET"])
def scholarship_view():
    scholarship = Aid.query.filter_by(aid_type='Scholarship').all()
    return render_template('scholarship_view.html', scholarship=scholarship)

@aid_bp.route('/grants', methods=["GET"])
def grant_view():
    grant = Aid.query.filter_by(aid_type='Grant').all()
    return render_template('grant_view.html', grant=grant)

@main_bp.route('/donor')
@login_required
def donor():
    return render_template('donor.html')

@main_bp.route('/financialAssistance', methods=['POST'])
@login_required
def application():
    return render_template("application_form.html")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == 'Admin':
                flash('Welcome Admin.', 'Success')
                return redirect(url_for('main.admin'))
            elif user.role == 'Student':
                flash("Student logged in")
                return redirect(url_for('main.student'))
            elif user.role == 'Donor':
                flash('Donor logged in successfully!')
                return redirect(url_for('main.donor'))
        else:
            return render_template('login.html', message='Invalid email or password.')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('password1')
        firstname = request.form.get('firstname')
        surname = request.form.get('surname')
        role = request.form.get('role')
        
        if password != confirm_password:
            flash("Passwords don't match!")
            return render_template('register.html')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('E-mail already exists. Please use a different e-mail.')
            return render_template('register.html')

        new_user = User(email=email, first_name=firstname, surname=surname, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))
