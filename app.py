from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
from werkzeug import *
from werkzeug.security import *
from datetime import *
from flask_mail import *
from sqlalchemy import *
from celery import *
from celery.schedules import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fantastic_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Fantastic 11'  


db = SQLAlchemy(app)

#We initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

#email message
app.config['MAIL_SERVER'] = 'smtp.googleemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'fansteleven@gmail.com'
app.config['MAIL_PASSWORD'] = 'fansteleven@11'

mail = Mail(app)

#-------------------------------------------------- Models ------------------------------------------------------------------------------------------------------
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer ,primary_key=True, autoincrement=True)
    email = db.Column(db.String(150) ,unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    surname = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    #methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)    


class Aid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    faculty = db.Column(db.String(80), nullable=False)
    aid_type = db.Column(db.String(80), nullable=False)
    aid_description = db.Column(db.String(1000), nullable=False)
    aid_requirements = db.Column(db.String(1000), nullable=False)
    aid_link = db.Column(db.String(255))
    upload_date = db.Column(db.Date)
    deadline_date = db.Column(db.Date)
    
    
class FinancialAssistance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    student_no = db.Column(db.String(8), nullable=False)
    cell_no = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    proof_of_reg = db.Column(LargeBinary)
    motivational = db.Column(LargeBinary)
    statement_of_acc = db.Column(LargeBinary)
    id_copy = db.Column(LargeBinary)

    def save_document(self, document_type, document_data):
        if document_type == 'proof_of_reg':
            self.proof_of_reg = document_data
        elif document_type == 'motivational':
            self.motivational = document_data
        elif document_type == 'statement_of_acc':
            self.statement_of_acc = document_data
        elif document_type == 'id_copy':
            self.id_copy = document_data
    
    
#-------------------------------------- end Models ------------------------------------------------------------------------------------------- 


#--------------------------------------- Routes -----------------------------------------------------------------------------------------------

#------ User routes -------------------------------------------
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/admin')
@login_required
def admin():
    return render_template("admin.html")


@app.route('/aid_bursary_list', )
def aid_bursary_list():    
    bursaries = Aid.query.filter_by(aid_type='Bursary').all()
    return render_template('aid_bursary_list.html', bursaries=bursaries)


@app.route('/aid_scholarship_list')
def aid_scholarship_list():
    scholar = Aid.query.filter_by(aid_type='Scholarship').all()
    return render_template("aid_scholarship_list.html", scholarship=scholar)


@app.route('/aid_grant_list')
def aid_grant_list():
    grant = Aid.query.filter_by(aid_type='Grant').all()
    return render_template("aid_grant_list.html", grant=grant)


@app.route('/student')
@login_required
def student():
    return render_template('student.html')


@app.route('/bursaries', methods=["GET"])
def bursary_view():
    bursaries = Aid.query.filter_by(aid_type='Bursary').all()
    return render_template('bursary_view.html', bursaries=bursaries)


@app.route('/scholarships', methods=["GET"])
def scholarship_view():
    scholarship = Aid.query.filter_by(aid_type='Scholarship').all()
    return render_template('scholarship_view.html', scholarship=scholarship)


@app.route('/grants', methods=["GET"])
def grant_view():
    grant = Aid.query.filter_by(aid_type='Grant').all()
    return render_template('grant_view.html', grant=grant)
 

@app.route('/donor')
@login_required
def donor():
    return render_template('donor.html')


@app.route('/financialAssistance', methods=['POST'])
@login_required
def application():
    return render_template("application_form.html")


#---------------------------------------------- Login -----------------------------------------------------------


# Load User-----------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def add_user(email, password, fname, sname, role):
# Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user is None:
        # Create a new user instance
        new_user = User(email=email,
                        first_name=fname,
                        surname=sname,
                        role=role)
        new_user.set_password(password)
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        print(f"User {fname} added successfully.")
    else:
        print(f"User {fname} already exists.")


# Login Code
@app.route('/login', methods=['GET', 'POST'])
def login():
    print(f"Request method: {request.method}")  # Add logging
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        print("Handling POST request")  # Additional logging
        if user and user.check_password(password):
            print("Check log-in")
            login_user(user)
            if user.role == 'Admin':
                flash('Welcome Admin.', 'Success')
                return redirect(url_for('admin'))
            
            elif user.role == 'Student':
                flash("Student logged in")
                return redirect(url_for('student'))
            
            elif user.role == 'Donor':
                flash('Donor logged in successfully!')
                return redirect(url_for('donor'))
            
        else:
            # If authentication fails, reload the login page with an error message
            return render_template('login.html', message='Invalid email or password.')
    return render_template('login.html')


# Register Code
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('password1')
        firstname = request.form.get('firstname')
        surname = request.form.get('surname')
        role = request.form.get('role')
        
        if password != confirm_password:
            # Passwords don't match
            flash("Passwords don't match!")
            return render_template('register.html')
        
        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            # If Email already exists:
            flash('E-mail already exists. Please use a different e-mail.')
            return render_template('register.html')

        # If email doesn't exist, continue with registration
        add_user(email, password, firstname, surname, role)

        # Redirect to login page
        return redirect(url_for('login'))  # Corrected redirect to use function name

    # Render the registration template if the method is GET
    return render_template('register.html')


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


# ------------------- end Logout -----------------------------------------------------


# --------------------- Uploads ----------------------------------------------------------


def add_aid(title, faculty, aid_type, aid_desc, aid_req, aid_link, up_date, dead_date):
# Check if bursary already exists
    existing_aid = Aid.query.filter_by(title=title).first()
    if existing_aid is None:
        # Create a new aid instance
        new_aid = Aid(title = title,
                        faculty = faculty,
                        aid_type = aid_type,
                        aid_description = aid_desc,
                        aid_requirements = aid_req,
                        aid_link = aid_link,
                        upload_date = up_date,
                        deadline_date = dead_date)
        # Add the new aid to the database
        db.session.add(new_aid)
        db.session.commit()
        print(f"Aid added successfully.")
    else:
        print(f"Aid already exists.")


#---------------------- End Routes --------------------------------------------------------------------------------------------------------------


with app.app_context():
    db.create_all()
    add_aid("Nedbank", "Arts and Design", "Bursary", "The best bursary in South Africa", "1. Matric \n2. Diploma or Degree", "https://google.com", datetime.utcnow().date(), datetime.utcnow().date())
    add_user('admin@gmail.com', 'fanadmin', 'Admin', 'Main', 'Admin')
    print("Db made")


if __name__ == '__main__':
    app.run(debug=True)