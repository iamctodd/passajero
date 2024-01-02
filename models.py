from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship

db = SQLAlchemy() 

# CONFIGURE DATABASE
class Entry(db.Model):
    __tablename__ = "passwords"
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(200), nullable=False)
    site_username = db.Column(db.String(75), nullable=False)
    site_password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by = relationship("User", back_populates="entries")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    last_updated = db.Column(db.DateTime)
    last_used = db.Column(db.DateTime)
    
    def __init__(self, site, site_username, site_password, current_user):
        self.site = site
        self.site_username = site_username
        self.site_password = site_password
        self.created_at = datetime.now()
        self.created_by = current_user
        self.last_updated = datetime.now()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    entries = relationship("Entry", back_populates="created_by")
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
