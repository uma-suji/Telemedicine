from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    specialization = db.Column(db.String(100))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    symptoms = db.Column(db.String(255))
    status = db.Column(db.String(50), default="Pending")  # ✅ Add this line
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('User', foreign_keys=[patient_id])
    doctor = db.relationship('User', foreign_keys=[doctor_id])





class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )

    doctor_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )

    appointment_date = db.Column(db.String(50), nullable=False)
    appointment_time = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="Booked")

    patient = db.relationship(
        "User", foreign_keys=[patient_id], backref="patient_appointments"
    )

    doctor = db.relationship(
        "User", foreign_keys=[doctor_id], backref="doctor_appointments"
    )
class PatientRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    age = db.Column(db.Integer)
    dob = db.Column(db.String(20))
    phone_number = db.Column(db.String(20))

    weight = db.Column(db.Float)   # kg
    height = db.Column(db.Float)   # cm

    blood_pressure = db.Column(db.String(20))
    heart_rate = db.Column(db.Integer)
    diagnosis = db.Column(db.Text) 
    prescription = db.Column(db.Text)
    nearby_pharmacy = db.Column(db.String(200))
    last_checkup = db.Column(db.DateTime)
    last_consultation = db.Column(db.DateTime)
    address = db.Column(db.Text)

    # relationships (VERY IMPORTANT)
    patient = db.relationship("User", foreign_keys=[patient_id])
    doctor = db.relationship("User", foreign_keys=[doctor_id])

class PatientVitals(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    blood_pressure = db.Column(db.String(20))
    heart_rate = db.Column(db.Integer)

    diagnosis = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)



