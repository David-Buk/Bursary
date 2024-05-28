from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    surname = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False)

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
    proof_of_reg = db.Column(db.LargeBinary)
    motivational = db.Column(db.LargeBinary)
    statement_of_acc = db.Column(db.LargeBinary)
    id_copy = db.Column(db.LargeBinary)

    def save_document(self, document_type, document_data):
        if document_type == 'proof_of_reg':
            self.proof_of_reg = document_data
        elif document_type == 'motivational':
            self.motivational = document_data
        elif document_type == 'statement_of_acc':
            self.statement_of_acc = document_data
        elif document_type == 'id_copy':
            self.id_copy = document_data
