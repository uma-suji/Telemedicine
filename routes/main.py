from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import User, Consultation, Appointment, PatientRecord
from datetime import datetime
from ai_model import predict_disease  # <-- fixed
import pickle
from sqlalchemy.orm import joinedload
main = Blueprint("main", __name__)

# ==========================
# HOME
# ==========================
@main.route("/")
def home():
    return render_template("home.html")


# ==========================
# PATIENT DASHBOARD
# ==========================
@main.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "patient":
        return redirect(url_for("main.doctor_dashboard"))

    consultations = Consultation.query.filter_by(patient_id=current_user.id).all()
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    record = PatientRecord.query.filter_by(patient_id=current_user.id).first()
    appointment = Appointment.query.filter_by(patient_id=current_user.id).first()

    doctors = User.query.filter_by(role="doctor").all()  # 🔥 ADD THIS

    return render_template(
        "patient_dashboard.html",
        consultations=consultations,
        appointments=appointments,
        record=record,
        appointment=appointment,
        doctors=doctors   # 🔥 PASS TO TEMPLATE
    )

# ==========================
# DOCTOR DASHBOARD
# ==========================
@main.route("/doctor-dashboard")
@login_required
def doctor_dashboard():
    if current_user.role != "doctor":
        return redirect(url_for("main.dashboard"))

    # Fetch all data for this doctor
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    consultations = Consultation.query.filter_by(doctor_id=current_user.id).all()
    records = PatientRecord.query.filter_by(doctor_id=current_user.id).all()

    return render_template(
        "doctor_dashboard.html",
        appointments=appointments,
        consultations=consultations,
        records=records
    )



# ==========================
# DOCTOR APPOINTMENTS PAGE
# ==========================
@main.route("/doctor-appointments")
@login_required
def doctor_appointments():
    if current_user.role != "doctor":
        return redirect(url_for("main.dashboard"))

    appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    return render_template("doctor_appointments.html", appointments=appointments)


# ==========================
# DOCTOR CONSULTATIONS PAGE
# ==========================
@main.route("/doctor-consultations")
@login_required
def doctor_consultations():
    if current_user.role != "doctor":
        return redirect(url_for("main.dashboard"))

    consultations = Consultation.query.filter_by(doctor_id=current_user.id).all()
    return render_template("doctor_consultations.html", consultations=consultations)


# ==========================
# NEW CONSULTATION (PATIENT)
# ==========================
@main.route("/new-consultation", methods=["GET", "POST"])
@login_required
def new_consultation():
    doctors = User.query.filter_by(role="doctor").all()

    if request.method == "POST":
        consultation = Consultation(
            patient_id=current_user.id,
            doctor_id=request.form.get("doctor_id"),
            symptoms=request.form.get("symptoms"),
            created_at=datetime.utcnow()
        )
        db.session.add(consultation)
        db.session.commit()

        flash("Consultation submitted", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("new_consultation.html", doctors=doctors)


# ==========================
# BOOK APPOINTMENT (PATIENT)
# ==========================
@main.route("/book-appointment", methods=["GET", "POST"])
@login_required
def book_appointment():
    doctors = User.query.filter_by(role="doctor").all()

    if request.method == "POST":
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=request.form.get("doctor_id"),
            appointment_date=request.form.get("appointment_date"),
            appointment_time=request.form.get("appointment_time")
        )
        db.session.add(appointment)
        db.session.commit()

        flash("Appointment booked successfully", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("book_appointment.html", doctors=doctors)


# ==========================
# ADD PATIENT RECORD (DOCTOR)
# ==========================
@main.route("/add-patient-record/<int:appointment_id>", methods=["GET", "POST"])
@login_required
def add_patient_record(appointment_id):
    if current_user.role != "doctor":
        return "Unauthorized", 403

    appointment = Appointment.query.get_or_404(appointment_id)
    patient = appointment.patient

    record = PatientRecord.query.filter_by(patient_id=patient.id).first()

    if request.method == "POST":
        # Save/update patient record
        if record:
            record.age = request.form.get("age")
            record.phone_number = request.form.get("phone_number")
            record.dob = request.form.get("dob")
            record.diagnosis = request.form.get("diagnosis")
            record.weight = request.form.get("weight")
            record.height = request.form.get("height")
            record.blood_pressure = request.form.get("blood_pressure")
            record.heart_rate = request.form.get("heart_rate")
            record.address = request.form.get("address")
            record.prescription = request.form.get("prescription")
            record.nearby_pharmacy = request.form.get("nearby_pharmacy")
            record.last_checkup = datetime.utcnow()
            record.last_consultation = datetime.utcnow()
            record.doctor_id = current_user.id
        else:
            record = PatientRecord(
                patient_id=patient.id,
                doctor_id=current_user.id,
                age=request.form.get("age"),
                phone_number=request.form.get("phone_number"),
                dob=request.form.get("dob"),
                diagnosis=request.form.get("diagnosis"),
                weight=request.form.get("weight"),
                height=request.form.get("height"),
                blood_pressure=request.form.get("blood_pressure"),
                heart_rate=request.form.get("heart_rate"),
                address=request.form.get("address"),
                prescription=request.form.get("prescription"),
                nearby_pharmacy=request.form.get("nearby_pharmacy"),
                last_checkup=datetime.utcnow(),
                last_consultation=datetime.utcnow()
            )
            db.session.add(record)

        # Mark appointment completed
        appointment.status = "Completed"
        # 🔹 Create Consultation History entry with full details
        details = (
    f"Phone: {request.form.get('phone_number')}, "
    f"Age: {request.form.get('age')}, "
    f"DOB: {request.form.get('dob')}, "
    f"Weight: {request.form.get('weight')} kg, "
    f"Height: {request.form.get('height')} cm, "
    f"BP: {request.form.get('blood_pressure')}, "
    f"HR: {request.form.get('heart_rate')}, "
    f"Diagnosis: {request.form.get('diagnosis')}, "
    f"Prescription: {request.form.get('prescription')}, "
    f"Pharmacy: {request.form.get('nearby_pharmacy')}"
)

        consultation = Consultation(
        patient_id=patient.id,
        doctor_id=current_user.id,
        symptoms=details,   # store full record here
        status="Completed",
        created_at=datetime.utcnow()
        )
        db.session.add(consultation)
        db.session.commit()


        flash("Patient record saved & consultation history updated!", "success")
        return redirect(url_for("main.doctor_appointments"))

    return render_template("add_patient_record.html", appointment=appointment, patient=patient, record=record)

# ==========================
# VIDEO CALL ROUTE
# ==========================
@main.route("/video-call/<int:appointment_id>")
@login_required
def video_call(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.patient_id != current_user.id and appointment.doctor_id != current_user.id:
        return "Unauthorized", 403

    return render_template("video_call.html", appointment=appointment)


# ==========================
# AI SYMPTOM CHECKER ROUTE
# ==========================
# Load trained model (already loaded inside ai_model.py)
# model = pickle.load(open("model/model.pkl", "rb"))

@main.route("/ai-symptom-checker", methods=["GET", "POST"])
@login_required
def ai_symptom_checker():
    if current_user.role != "patient":
        return redirect(url_for("main.doctor_dashboard"))

    result = None
    if request.method == "POST":
        symptoms = request.form.get("symptoms")
        if symptoms:
            result = predict_disease(symptoms)  # fixed function call

    return render_template("ai_symptom_checker.html", result=result)

# ==========================
# DELETE CONSULTATION (Patient)
# ==========================
@main.route("/delete-consultation/<int:consultation_id>", methods=["POST", "GET"])
@login_required
def delete_consultation(consultation_id):
    consultation = Consultation.query.get_or_404(consultation_id)

    if consultation.patient_id != current_user.id:
        return "Unauthorized", 403

    db.session.delete(consultation)
    db.session.commit()

    flash("Consultation deleted successfully", "success")
    return redirect(url_for("main.dashboard"))


# ==========================
# LIST OF DOCTORS
# ==========================
@main.route("/doctors")
@login_required
def doctors_list():
    if current_user.role != "patient":
        return redirect(url_for("main.doctor_dashboard"))

    doctors = User.query.filter_by(role="doctor").all()
    return render_template("doctors_list.html", doctors=doctors)

@main.route("/complete-consultation/<int:consultation_id>", methods=["POST"])
@login_required
def complete_consultation(consultation_id):
    if current_user.role != "doctor":
        return "Unauthorized", 403

    # Get consultation
    consultation = Consultation.query.get_or_404(consultation_id)
    patient_id = consultation.patient_id
    doctor_id = current_user.id

    # Check if a patient record already exists
    record = PatientRecord.query.filter_by(patient_id=patient_id).first()

    if record:
        # Update existing record
        record.last_checkup = datetime.utcnow()
        record.last_consultation = datetime.utcnow()
        record.doctor_id = doctor_id  # latest doctor
    else:
        # Create new record if first time
        new_record = PatientRecord(
            patient_id=patient_id,
            doctor_id=doctor_id,
            last_checkup=datetime.utcnow(),
            last_consultation=datetime.utcnow()
        )
        db.session.add(new_record)

    # Mark consultation as completed
    consultation.status = "Completed"

    db.session.commit()

    flash("Consultation completed and patient record updated!", "success")
    return redirect(url_for("main.doctor_consultations"))


@main.route("/patient-video-calls")
@login_required
def patient_video_calls():
    appointments = Appointment.query.filter_by(
        patient_id=current_user.id,
        status="Booked"
    ).all()

    return render_template("patient_video_calls.html", appointments=appointments)


    # ==========================
# PATIENT CONSULTATION HISTORY
# ==========================
@main.route("/patient-history")
@login_required
def patient_history():
    if current_user.role != "patient":
        return redirect(url_for("main.doctor_dashboard"))

    consultations = Consultation.query.filter_by(patient_id=current_user.id).all()
    return render_template("patient_history.html", consultations=consultations)



@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/contact")
def contact():
    return render_template("contact.html")

@main.route("/services")
def services():
    return render_template("services.html")

@main.route("/patient-details/<int:patient_id>")
@login_required
def patient_details(patient_id):
    record = PatientRecord.query.filter_by(patient_id=patient_id).first()
    consultations = Consultation.query.filter_by(patient_id=patient_id).all()
    return render_template("patient_details.html", record=record, consultations=consultations)
