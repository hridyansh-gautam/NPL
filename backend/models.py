from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class user(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class uploadedFiles(db.Model):
    file_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    conversion_status = db.Column(db.Boolean, nullable=False, default=False)